# slack_mail_notifier

    Slack の未読メッセージをメール通知するSlack App
    メールサーバはAmazon SES
    通知間隔は1時間
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

# 要素技術

    - Python3.6 ... 実装
    - Slack API ... メッセージ取得
    - AWS Lambda ... 実行サーバ
    - AWS SES ... メール通知
    - AWS CloudWatch Event ... 定期実行
    - AWS DynamoDB ... 状態保存
    - AWS CloudFormation ... デプロイ
    - Vagrant ... 開発
    - Docker ... 開発
    - Ramen ... 癒やし

# ToDo

    - チャンネルURL含める
    - メールのテンプレート化
    - 複数チャンネル対応?

# 備考

    ワークスペースが多いとタブで開いておくのも場所取るため、閉じておきたい。
    ただ閉じてしまうと新着メッセージに気付かない。
    ならばと未読メッセージをメール通知してくれるスクリプトを書いてみた。

    動くようにしてから気付いたのは通知させたいワークスペースの管理者権限を持っていない事だった。
    アプリのインストールが出来ぬ。
