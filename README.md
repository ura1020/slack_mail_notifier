# slack_mail_notifier

    Slack の未読メッセージをメール通知してくれるSlack App
    メールサーバはAmazon SESの想定
    CloudWatch Eventで定期実行の想定

# 設定手順
    - Slack Appに登録
    - AWS Lambdaにデプロイ。要環境変数設定。
    - AWS CloudWatchで定期実行設定

# 環境変数
    - S3_BUCKET
      デプロイ時に使用するs3バケット名
    - SLACK_TOKEN
      SlackAPIを叩くのに使用するトークン
    - SLACK_CHANNEL
      取得対象Slackチャンネル
    - TO_ADDRESS
      通知先Eメールアドレス
    - SOURCE_ADDRESS
      通知元Eメールアドレス(AWS SESで要導通)


# ToDo

    - 連続通知抑止

# 備考

    ワークスペースが多いとタブで開いておくのも場所取るため、閉じておきたい。
    ただ閉じてしまうと新着メッセージに気付かない。
    ならばと未読メッセージをメール通知してくれるスクリプトを書いてみた。

    動くようにしてから気付いたのは通知させたいワークスペースの管理者権限を持っていない事だった。
    アプリのインストールが出来ぬ。
