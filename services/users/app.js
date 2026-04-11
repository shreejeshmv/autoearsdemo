'use strict';

const express = require('express');
const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, GetCommand, PutCommand, UpdateCommand, DeleteCommand, ScanCommand } = require('@aws-sdk/lib-dynamodb');

const app = express();
app.use(express.json());

const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);
const TABLE_NAME = process.env.USERS_TABLE;

// GET /users - list all users
app.get('/users', async (req, res) => {
  try {
    const result = await docClient.send(new ScanCommand({ TableName: TABLE_NAME }));
    res.status(200).json(result.Items || []);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /users/:id - get user by id
app.get('/users/:id', async (req, res) => {
  try {
    const result = await docClient.send(new GetCommand({
      TableName: TABLE_NAME,
      Key: { id: req.params.id }
    }));
    if (!result.Item) {
      return res.status(404).json({ error: 'User not found' });
    }
    res.status(200).json(result.Item);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /users - create user
app.post('/users', async (req, res) => {
  const { name, email } = req.body || {};
  if (!name || !email) {
    return res.status(400).json({ error: 'name and email are required' });
  }
  const user = {
    id: crypto.randomUUID(),
    name,
    email,
    createdAt: new Date().toISOString()
  };
  try {
    await docClient.send(new PutCommand({ TableName: TABLE_NAME, Item: user }));
    res.status(201).json(user);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// PUT /users/:id - update user
app.put('/users/:id', async (req, res) => {
  const { name, email } = req.body || {};
  try {
    const existing = await docClient.send(new GetCommand({
      TableName: TABLE_NAME,
      Key: { id: req.params.id }
    }));
    if (!existing.Item) {
      return res.status(404).json({ error: 'User not found' });
    }
    const updated = { ...existing.Item };
    if (name !== undefined) updated.name = name;
    if (email !== undefined) updated.email = email;
    await docClient.send(new PutCommand({ TableName: TABLE_NAME, Item: updated }));
    res.status(200).json(updated);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE /users/:id - delete user
app.delete('/users/:id', async (req, res) => {
  try {
    const existing = await docClient.send(new GetCommand({
      TableName: TABLE_NAME,
      Key: { id: req.params.id }
    }));
    if (!existing.Item) {
      return res.status(404).json({ error: 'User not found' });
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
