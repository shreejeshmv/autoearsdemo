'use strict';

const express = require('express');
const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, GetCommand, PutCommand, DeleteCommand, ScanCommand } = require('@aws-sdk/lib-dynamodb');

const app = express();
app.use(express.json());

const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);
const TABLE_NAME = process.env.NOTIFICATIONS_TABLE;

// GET /notifications - list all notifications, optional ?userId= filter
app.get('/notifications', async (req, res) => {
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

// GET /notifications/:id - get notification by id
app.get('/notifications/:id', async (req, res) => {
  try {
    const result = await docClient.send(new GetCommand({
      TableName: TABLE_NAME,
      Key: { id: req.params.id }
    }));
    if (!result.Item) {
      return res.status(404).json({ error: 'Notification not found' });
    }
    res.status(200).json(result.Item);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /notifications - create notification
app.post('/notifications', async (req, res) => {
  const { userId, message } = req.body || {};
  if (!userId || !message) {
    return res.status(400).json({ error: 'userId and message are required' });
  }
  const notification = {
    id: crypto.randomUUID(),
    userId,
    message,
    read: false,
    createdAt: new Date().toISOString()
  };
  try {
    await docClient.send(new PutCommand({ TableName: TABLE_NAME, Item: notification }));
    res.status(201).json(notification);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// PUT /notifications/:id - update notification
app.put('/notifications/:id', async (req, res) => {
  const { message, read, userId } = req.body || {};
  try {
    const existing = await docClient.send(new GetCommand({
      TableName: TABLE_NAME,
      Key: { id: req.params.id }
    }));
    if (!existing.Item) {
      return res.status(404).json({ error: 'Notification not found' });
    }
    const updated = { ...existing.Item };
    if (message !== undefined) updated.message = message;
    if (read !== undefined) updated.read = read;
    if (userId !== undefined) updated.userId = userId;
    await docClient.send(new PutCommand({ TableName: TABLE_NAME, Item: updated }));
    res.status(200).json(updated);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE /notifications/:id - delete notification
app.delete('/notifications/:id', async (req, res) => {
  try {
    const existing = await docClient.send(new GetCommand({
      TableName: TABLE_NAME,
      Key: { id: req.params.id }
    }));
    if (!existing.Item) {
      return res.status(404).json({ error: 'Notification not found' });
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
