'use strict';

const express = require('express');
const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, GetCommand, PutCommand, DeleteCommand, ScanCommand } = require('@aws-sdk/lib-dynamodb');

const app = express();
app.use(express.json());

const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);
const TABLE_NAME = process.env.TASKS_TABLE;

// GET /tasks - list all tasks, optional ?userId= filter
app.get('/tasks', async (req, res) => {
  try {
    const { userId } = req.query;
    let params = { TableName: TABLE_NAME };
    if (userId) {
      params.FilterExpression = 'userId = :uid';
      params.ExpressionAttributeValues = { ':uid': userId };
    }
    const result = await docClient.send(new ScanCommand(params));
    res.status(200).json(result.Items || []);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /tasks/:id - get task by id
app.get('/tasks/:id', async (req, res) => {
  try {
    const result = await docClient.send(new GetCommand({
      TableName: TABLE_NAME,
      Key: { id: req.params.id }
    }));
    if (!result.Item) {
      return res.status(404).json({ error: 'Task not found' });
    }
    res.status(200).json(result.Item);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /tasks - create task
app.post('/tasks', async (req, res) => {
  const { title, description, status, userId } = req.body || {};
  if (!title || !userId) {
    return res.status(400).json({ error: 'title and userId are required' });
  }
  const task = {
    id: crypto.randomUUID(),
    title,
    description: description || '',
    status: status || 'pending',
    userId,
    createdAt: new Date().toISOString()
  };
  try {
    await docClient.send(new PutCommand({ TableName: TABLE_NAME, Item: task }));
    res.status(201).json(task);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// PUT /tasks/:id - update task
app.put('/tasks/:id', async (req, res) => {
  const { title, description, status, userId } = req.body || {};
  try {
    const existing = await docClient.send(new GetCommand({
      TableName: TABLE_NAME,
      Key: { id: req.params.id }
    }));
    if (!existing.Item) {
      return res.status(404).json({ error: 'Task not found' });
    }
    const updated = { ...existing.Item };
    if (title !== undefined) updated.title = title;
    if (description !== undefined) updated.description = description;
    if (status !== undefined) updated.status = status;
    if (userId !== undefined) updated.userId = userId;
    await docClient.send(new PutCommand({ TableName: TABLE_NAME, Item: updated }));
    res.status(200).json(updated);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE /tasks/:id - delete task
app.delete('/tasks/:id', async (req, res) => {
  try {
    const existing = await docClient.send(new GetCommand({
      TableName: TABLE_NAME,
      Key: { id: req.params.id }
    }));
    if (!existing.Item) {
      return res.status(404).json({ error: 'Task not found' });
    }
    await docClient.send(new DeleteCommand({
      TableName: TABLE_NAME,
      Key: { id: req.params.id }
    }));
    res.status(204).send();
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = app;
