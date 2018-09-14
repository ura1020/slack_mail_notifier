#!/bin/sh

deploy_name=SlackMailNotifier
s3_bucket=${S3_BUCKET}
archives_dir=archives

cd `dirname $0`

# アーカイブ
mkdir $archives_dir || true
resource_name=${deploy_name}.lambda_function.zip
find . | grep -E "(__pycache__|\.pyc$|\.pyo$|\.DS_Store$)" | xargs rm -rf
zip -9 -x "*.git*" -x "*boto3*" -x "*botocore*" -x "*$archives_dir*" -r $archives_dir/$resource_name .

# アップロード
aws s3 cp $archives_dir/$resource_name s3://$s3_bucket/ \
  --acl bucket-owner-full-control

sed -e "s/{SLACK_TOKEN}/${SLACK_TOKEN}/g" -e "s/{SLACK_CHANNEL}/${SLACK_CHANNEL}/g" -e "s/{TO_ADDRESS}/${TO_ADDRESS}/g" -e "s/{SOURCE_ADDRESS}/${SOURCE_ADDRESS}/g" -e "s/{S3_BUCKET}/${s3_bucket}/g" -e "s/{S3_KEY}/${resource_name}/g" cloudformation.tpl > cloudformation.yml

# デプロイ
# aws cloudformation delete-stack \
#   --stack-name ${deploy_name}

# aws cloudformation create-stack \
#   --stack-name ${deploy_name} \
#   --template-body file://cloudformation.yml \
#   --capabilities CAPABILITY_IAM

# aws cloudformation update-stack \
#   --stack-name ${deploy_name} \
#   --template-body file://cloudformation.yml \
#   --capabilities CAPABILITY_IAM

aws cloudformation deploy \
  --stack-name ${deploy_name} \
  --template cloudformation.yml \
  --capabilities CAPABILITY_IAM
