# AutoEars Demo - Users & Tasks Microservices

Two-service microservices application built with Node.js/Express on AWS Lambda, backed by DynamoDB, and exposed via API Gateway HTTP APIs. Infrastructure is defined with AWS CDK (TypeScript).

## Architecture

```
                        ┌─────────────────────────────────────────┐
                        │              AWS Cloud                   │
                        │                                          │
  Client ──► API GW ──► │  Lambda (Users)  ──► DynamoDB (Users)   │
             HTTP API   │                                          │
                        │  Lambda (Tasks)  ──► DynamoDB (Tasks)   │
             HTTP API ──► │                                          │
                        └─────────────────────────────────────────┘
```

## Project Structure

```
autoearsdemo/
├── services/
│   ├── users/
│   │   ├── app.js          # Express app with CRUD routes
│   │   ├── handler.js      # Lambda entry point
│   │   └── package.json
│   └── tasks/
│       ├── app.js          # Express app with CRUD routes
│       ├── handler.js      # Lambda entry point
│       └── package.json
├── infra/
│   ├── bin/
│   │   └── app.ts          # CDK app entry point
│   ├── lib/
│   │   └── autoearsdemo-stack.ts  # CDK stack definition
│   ├── cdk.json
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

## Users API Endpoints

| Method | Path         | Description          | Status Codes        |
|--------|--------------|----------------------|---------------------|
| GET    | /users       | List all users       | 200                 |
| GET    | /users/:id   | Get user by ID       | 200, 404            |
| POST   | /users       | Create a user        | 201, 400            |
| PUT    | /users/:id   | Update a user        | 200, 404            |
| DELETE | /users/:id   | Delete a user        | 204, 404            |

User schema: `{ id, name, email, createdAt }`

Required fields on POST: `name`, `email`

## Tasks API Endpoints

| Method | Path         | Description                              | Status Codes        |
|--------|--------------|------------------------------------------|---------------------|
| GET    | /tasks       | List all tasks (supports `?userId=` filter) | 200              |
| GET    | /tasks/:id   | Get task by ID                           | 200, 404            |
| POST   | /tasks       | Create a task                            | 201, 400            |
| PUT    | /tasks/:id   | Update a task                            | 200, 404            |
| DELETE | /tasks/:id   | Delete a task                            | 204, 404            |

Task schema: `{ id, title, description, status, userId, createdAt }`

Status values: `pending` | `in_progress` | `done`

Required fields on POST: `title`, `userId`

Filter by user: `GET /tasks?userId=<userId>`

## Prerequisites

- Node.js 18+
- AWS CLI configured with appropriate credentials
- AWS CDK v2: `npm install -g aws-cdk`

## Deployment

1. Install dependencies for each service:

```bash
cd services/users && npm install
cd ../tasks && npm install
```

2. Install and build CDK infrastructure:

```bash
cd infra
npm install
npm run build
```

3. Bootstrap CDK (first time only):

```bash
cdk bootstrap
```

4. Deploy the stack:

```bash
cdk deploy
```

The deployment outputs the API URLs for both services.

## Environment Variables

| Variable    | Service | Description                        |
|-------------|---------|------------------------------------|
| USERS_TABLE | Users   | DynamoDB table name for users data |
| TASKS_TABLE | Tasks   | DynamoDB table name for tasks data |

These are automatically set by the CDK stack when deploying.
