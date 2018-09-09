import os
import requests

def lambda_handler(event, context):

  def getEnviron(key):
    if not key in os.environ:
      print("export %s=<your setting>" % key)
      exit()

    return os.environ[key]

  token = getEnviron('SLACK_TOKEN')
  channel = getEnviron('SLACK_CHANNEL')
  to_addressses = [getEnviron('TO_ADDRESS')]
  source_address = getEnviron('SOURCE_ADDRESS')

  CHARSET = "UTF-8"
  AWS_REGION = "us-west-2"

  def getSlackApi(url,response={}):
    # print("request:%s" % url)
    result = requests.get(url,timeout=5).json()
    # print("response:%s" % result)
    result = {**{"ok":False},**response,**result} # like $.extend
    return result if result["ok"] else False

  # チャンネルのメッセージ履歴取得
  result = getSlackApi(
    url="https://slack.com/api/channels.history?token=%s&channel=%s&unreads=true" % (token,channel),
    response={"messages":[],"unread_count_display":0})
  if not result:
    return {"statusCode": 502} # Bad Gateway

  # デバッグ
  # result["messages"] = [{"user":"U02HRP1AU","type":"message","text":"AAAA"},{"user":"U0JMASR52","type":"message","text":"BBBB"},{"user":"U02HRP1AU","type":"message","text":"CCCC"}]
  # result["unread_count_display"] = 2

  unreads = [{"user":message["user"],"text":message["text"]} for message in result["messages"][:result["unread_count_display"]] if message["type"] == "message"]
  if not unreads:
    return {"statusCode": 200} # 未読なし
  # print(unreads)

  # チャンネルのユーザリスト取得
  result = getSlackApi(
    url="https://slack.com/api/users.list?token=%s&channel=%s" % (token,channel),
    response={"members":[]})
  if not result:
    return {"statusCode": 502} # Bad Gateway

  print(result)
  members = {member["id"]:{"name":member["name"]} for member in result["members"]}

  for unread in unreads:
    unread["name"] = members[unread["user"]]["name"] if unread["user"] in members else "unknown"
  # print(unreads)

  def sendEmail(unreads):
    def json2str(source):
      import json
      return json.dumps(source,ensure_ascii=False,indent=4)

    from datetime import datetime, timedelta, timezone
    jst = timezone(timedelta(hours=+9), 'JST')
    str_now = datetime.now(jst).strftime('%Y-%m-%dT%H:%M:%SZ')
    print(str_now)

    import boto3
    ses = boto3.client("ses",region_name=AWS_REGION)
    ses.send_email(
      Source=source_address,
      Destination={
          'ToAddresses':to_addressses
      },
      Message={
          'Subject': {
              'Data': "Slack unread messagers at %s" % str_now,
              'Charset': CHARSET
          },
          'Body': {
              'Text': {
                  'Data': json2str(unreads),
                  'Charset': CHARSET
              }
          }
      }
    )

  sendEmail(unreads)

  return {
      "statusCode": 200,
      "unreads": unreads
  }

if __name__ == "__main__":
  lambda_handler({},{})
