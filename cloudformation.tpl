AWSTemplateFormatVersion: '2010-09-09'
Description: 'Scheduled Lambda Sample'
Parameters:
  SlackToken:
    Type: String
    Default: {SLACK_TOKEN}
  SlackChannel:
    Type: String
    Default: {SLACK_CHANNEL}
  ToAddress:
    Type: String
    Default: {TO_ADDRESS}
  SourceAddress:
    Type: String
    Default: {SOURCE_ADDRESS}
  S3Key:
    Type: String
    Default: {S3_KEY}
Resources:
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
        - Effect: Allow
          Principal:
            Service:
            - lambda.amazonaws.com
          Action:
          - sts:AssumeRole
      Path: /
      Policies:
      - PolicyName: root
        PolicyDocument:
          Version: '2012-10-17'
          Statement:
          - Effect: Allow
            Action:
            - logs:CreateLogGroup
            - logs:CreateLogStream
            - logs:PutLogEvents
            Resource: '*'
  LambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      Handler: index.lambda_handler
      Role: !GetAtt LambdaExecutionRole.Arn
      Code:
        S3Bucket: packages-ura1020
        S3Key: !Ref 'S3Key'
      Runtime: python3.6
      MemorySize: 128
      Timeout: 30
      Description: 'Scheduled Lambda Sample (python3 urlopen)'
      Environment:
        Variables:
          'SLACK_TOKEN': !Ref 'SlackToken'
          'SLACK_CHANNEL': !Ref 'SlackChannel'
          'TO_ADDRESS': !Ref 'ToAddress'
          'SOURCE_ADDRESS': !Ref 'SourceAddress'
      Tags:
      - Key: Name
        Value: 'ScheduledLambdaSample'
      - Key: CloudformationArn
        Value: !Ref 'AWS::StackId'
  ScheduledRule:
    Type: AWS::Events::Rule
    Properties:
      Description: ScheduledRule
      ScheduleExpression: 'cron(0 0/1 * * ? *)'
      State: ENABLED
      Targets:
      - Arn: !GetAtt 'LambdaFunction.Arn'
        Id: TargetFunctionV1
  PermissionForEventsToInvokeLambda:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref 'LambdaFunction'
      Action: lambda:InvokeFunction
      Principal: events.amazonaws.com
      SourceArn: !GetAtt 'ScheduledRule.Arn'
