# QOTD

Serverless project to automatically send a quote of the day to subscribers using Lambda and SNS

## Services covered:

EventBridge | IAM | Lambda | SNS

## Prerequisites:

- Installed [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- Ran sam init && sam deploy --guided

## Template explanation:

## Section 1:

Set the memory and timeout value for the Lambda function. I increased this from the default 3 seconds timeout while troubleshooting an issue with the json response

This section also references an SSM parameter for the subscriber email which was manually created through the console. This part could also have been completed from inside this template

```
Globals:
  Function:
    Timeout: 10
    MemorySize: 128

Parameters:
  Email:
    Type: AWS::SSM::Parameter::Value<String>
    Default: '/dev/subscriber-email'
    Description: The email address to receive alerts

```

## Section 2

Create the SNS topic and specify the subscriber

```
  QotdTopic:
    Type: AWS::SNS::Topic

  AlarmSubscriberEmail:
    Type: AWS::SNS::Subscription
    Properties:
      Endpoint: !Ref Email
      Protocol: email
      TopicArn: !Ref QotdTopic

```

## Section 3

Create the Lambda function and EventBridge rule. The Lambda function code is in the getFunction/index.py file

The EventBridge rule was set to trigger the Lambda function daily at 8am EST 

```
#Section 3
  GetFunction:
    Type: AWS::Serverless::Function
    Properties:
      Role: !GetAtt GetFunctionRole.Arn 
      CodeUri: getFunction/
      Handler: index.lambda_handler
      Runtime: python3.9
      Architectures:
        - x86_64
      Environment:
        Variables:
          REGION: !Ref AWS::Region
          TOPIC: !Ref QotdTopic

  #EventBridge rule to trigger function every day at 8am EST          
  ScheduledFunction:
    Type: AWS::Events::Rule
    Properties: 
      ScheduleExpression: cron(0 15 * * ? *)
      State: ENABLED
      Targets: 
        - Arn: !GetAtt GetFunction.Arn
          Id: GetFunction

```

## Section 4

Create IAM role to allow Lambda to publish to SNS. A managed AWS policy is used here to allow Lambda write access to CloudWatch logs.

This sections also adds permission to allow EventBridge to invoke the Lambda function.

```
  GetFunctionRole:
    Type: AWS::IAM::Role 
    Properties:
      AssumeRolePolicyDocument:
        Version: 2012-10-17
        Statement: 
          - Effect: Allow
            Action: sts:AssumeRole 
            Principal:
              Service:
                - lambda.amazonaws.com
      Path: /
      Policies:
        - PolicyName: SNSPublish
          PolicyDocument: 
            Version: 2012-10-17
            Statement:
              - Effect: Allow
                Action:
                  - sns:Publish
                Resource:
                  - !Ref QotdTopic
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
 
  EventsPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref GetFunction
      Action: lambda:InvokeFunction
      Principal: events.amazonaws.com
      SourceArn: !GetAtt ScheduledFunction.Arn

```


## Challenges & Troubleshooting

- I experienced errors while trying to use the requests module with Lamda. I was able to resolve this by opting for the urllib3 module instead.

- Test Lambda function locally:

`sam local invoke getFunction --event /events/event.json`

- View Lambda function logs:

`sam logs -n getFunction --stack-name qotd-stack --tail`

- Validate Cloudformation templates:

`cfn-lint template.yml` and/or `sam validate`



