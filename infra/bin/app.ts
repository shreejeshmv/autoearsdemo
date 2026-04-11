#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { AutoEarsDemoStack } from '../lib/autoearsdemo-stack';

const app = new cdk.App();
new AutoEarsDemoStack(app, 'AutoEarsDemoStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});
