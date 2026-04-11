import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as apigwv2 from 'aws-cdk-lib/aws-apigatewayv2';
import { HttpLambdaIntegration } from 'aws-cdk-lib/aws-apigatewayv2-integrations';

export class AutoEarsDemoStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // DynamoDB - Users table
    const usersTable = new dynamodb.Table(this, 'UsersTable', {
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // DynamoDB - Tasks table
    const tasksTable = new dynamodb.Table(this, 'TasksTable', {
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    tasksTable.addGlobalSecondaryIndex({
      indexName: 'userId-index',
      partitionKey: { name: 'userId', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // Lambda - Users
    const usersLambda = new lambda.Function(this, 'UsersFunction', {
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset('../services/users'),
      environment: {
        USERS_TABLE: usersTable.tableName,
      },
    });

    // Lambda - Tasks
    const tasksLambda = new lambda.Function(this, 'TasksFunction', {
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset('../services/tasks'),
      environment: {
        TASKS_TABLE: tasksTable.tableName,
      },
    });

    // Grant DynamoDB permissions
    usersTable.grantReadWriteData(usersLambda);
    tasksTable.grantReadWriteData(tasksLambda);

    // HTTP API - Users
    const usersIntegration = new HttpLambdaIntegration('UsersIntegration', usersLambda);
    const usersApi = new apigwv2.HttpApi(this, 'UsersApi', {
      apiName: 'users-api',
    });

    usersApi.addRoutes({ path: '/users', methods: [apigwv2.HttpMethod.GET], integration: usersIntegration });
    usersApi.addRoutes({ path: '/users/{id}', methods: [apigwv2.HttpMethod.GET], integration: usersIntegration });
    usersApi.addRoutes({ path: '/users', methods: [apigwv2.HttpMethod.POST], integration: usersIntegration });
    usersApi.addRoutes({ path: '/users/{id}', methods: [apigwv2.HttpMethod.PUT], integration: usersIntegration });
    usersApi.addRoutes({ path: '/users/{id}', methods: [apigwv2.HttpMethod.DELETE], integration: usersIntegration });

    // HTTP API - Tasks
    const tasksIntegration = new HttpLambdaIntegration('TasksIntegration', tasksLambda);
    const tasksApi = new apigwv2.HttpApi(this, 'TasksApi', {
      apiName: 'tasks-api',
    });

    tasksApi.addRoutes({ path: '/tasks', methods: [apigwv2.HttpMethod.GET], integration: tasksIntegration });
    tasksApi.addRoutes({ path: '/tasks/{id}', methods: [apigwv2.HttpMethod.GET], integration: tasksIntegration });
    tasksApi.addRoutes({ path: '/tasks', methods: [apigwv2.HttpMethod.POST], integration: tasksIntegration });
    tasksApi.addRoutes({ path: '/tasks/{id}', methods: [apigwv2.HttpMethod.PUT], integration: tasksIntegration });
    tasksApi.addRoutes({ path: '/tasks/{id}', methods: [apigwv2.HttpMethod.DELETE], integration: tasksIntegration });

    // DynamoDB - Notifications table
    const notificationsTable = new dynamodb.Table(this, 'NotificationsTable', {
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Lambda - Notifications
    const notificationsLambda = new lambda.Function(this, 'NotificationsFunction', {
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset('../services/notifications'),
      environment: {
        NOTIFICATIONS_TABLE: notificationsTable.tableName,
      },
    });

    // Grant DynamoDB permissions
    notificationsTable.grantReadWriteData(notificationsLambda);

    // HTTP API - Notifications
    const notificationsIntegration = new HttpLambdaIntegration('NotificationsIntegration', notificationsLambda);
    const notificationsApi = new apigwv2.HttpApi(this, 'NotificationsApi', {
      apiName: 'notifications-api',
    });

    notificationsApi.addRoutes({ path: '/notifications', methods: [apigwv2.HttpMethod.GET], integration: notificationsIntegration });
    notificationsApi.addRoutes({ path: '/notifications/{id}', methods: [apigwv2.HttpMethod.GET], integration: notificationsIntegration });
    notificationsApi.addRoutes({ path: '/notifications', methods: [apigwv2.HttpMethod.POST], integration: notificationsIntegration });
    notificationsApi.addRoutes({ path: '/notifications/{id}', methods: [apigwv2.HttpMethod.PUT], integration: notificationsIntegration });
    notificationsApi.addRoutes({ path: '/notifications/{id}', methods: [apigwv2.HttpMethod.DELETE], integration: notificationsIntegration });

    // Outputs
    new cdk.CfnOutput(this, 'UsersApiUrl', {
      value: usersApi.url ?? '',
      description: 'Users API URL',
    });

    new cdk.CfnOutput(this, 'TasksApiUrl', {
      value: tasksApi.url ?? '',
      description: 'Tasks API URL',
    });

    new cdk.CfnOutput(this, 'NotificationsApiUrl', {
      value: notificationsApi.url ?? '',
      description: 'Notifications API URL',
    });
  }
}
