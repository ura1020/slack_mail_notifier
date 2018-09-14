import os
import requests
import boto3

CHARSET = "UTF-8"
AWS_REGION = "us-west-2"

def awsSesClient():
  return boto3.client("ses",region_name=AWS_REGION)

def awsDynamoTable(env,key):
  # ワンソース優先にした。ちょっとトリッキーか
  tablename = "%s.SlackMailNotifier.Unreads" % env
  pkname = "envChannelID"

  table = boto3.resource('dynamodb').Table(tablename)
  def get():
    result = table.get_item(Key={pkname:key})
    return result['Item'] if 'Item' in result else None

  def put(params):
    item = {pkname:key}
    item.update(params)
    table.put_item(Item=item)

  return {
    "get":get,
    "put":put
  }

def lambda_handler(event, context):
  def getEnviron(key,value=None):
    if not key in os.environ:
      if value is None:
        print("export %s=<your setting>" % key)
        exit()
      else:
        os.environ[key] = value

    return os.environ[key]

  env = getEnviron('ENV')
  token = getEnviron('SLACK_TOKEN')
  channel = getEnviron('SLACK_CHANNEL')
  to_addressses = [getEnviron('TO_ADDRESS')]
  source_address = getEnviron('SOURCE_ADDRESS')

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

  if getEnviron('DEBUG',""):
    # デバッグ用
    result["messages"] = [
      {"user":"U02HRP1AU","type":"message","text":"AAAA","client_msg_id":"test3"},
      {"user":"U0JMASR52","type":"message","text":"BBBB","client_msg_id":"test2"},
      {"user":"U02HRP1AU","type":"message","text":"CCCC","client_msg_id":"test1"}
    ]
    result["unread_count_display"] = 2
  print(result)

  unreads = [{key:message[key] for key in ["user","text","client_msg_id"]} for message in result["messages"][:result["unread_count_display"]] if message["type"] == "message"]
  if not unreads:
    return {"statusCode": 200} # 未読なし
  print(unreads)

  # チャンネルのユーザリスト取得
  result = getSlackApi(
    url="https://slack.com/api/users.list?token=%s&channel=%s" % (token,channel),
    response={"members":[]})
  if not result:
    return {"statusCode": 502} # Bad Gateway

  # print(result)
  members = {member["id"]:{"name":member["name"]} for member in result["members"]}

  for unread in unreads:
    unread["name"] = members[unread["user"]]["name"] if unread["user"] in members else "unknown"
  # print(unreads)

  # 未送信チェック
  table = awsDynamoTable(env,channel)
  latest = table["get"]()
  if latest and unreads[0]["client_msg_id"] == latest["client_msg_id"]:
    return {"statusCode": 200} # 未読メッセージは通知済み

  # 最新メッセージIDが更新されているので再送防止のためDynamoDBに保存
  table["put"]({"client_msg_id":unreads[0]["client_msg_id"]})

  def sendEmail(unreads):
    def json2str(source):
      import json
      return json.dumps(source,ensure_ascii=False,indent=4)

    from datetime import datetime, timedelta, timezone
    jst = timezone(timedelta(hours=+9), 'JST')
    str_now = datetime.now(jst).strftime('%Y-%m-%dT%H:%M:%SZ')
    print(str_now)

    ses = awsSesClient()
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
  print(lambda_handler({},{}))
