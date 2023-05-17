const { Configuration, OpenAIApi } = require("openai");
const { Client, GatewayIntentBits } = require("discord.js");
const { joinVoiceChannel } = require("@discordjs/voice");
const { addSpeechEvent } = require("discord-speech-recognition");

const fs = require('fs');
const path = require('path');
const config = require('../config.json');

const client = new Client({
  intents: [
    GatewayIntentBits.GuildVoiceStates,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.Guilds,
    GatewayIntentBits.MessageContent,
  ],
});


const configuration = new Configuration({
  apiKey: config.openai_key,
});

const openai = new OpenAIApi(configuration);

addSpeechEvent(client);
let lastMsgTime;
let currConvoFile;

client.on("messageCreate", (msg) => {
  const voiceChannel = msg.member?.voice.channel;
  if (voiceChannel) {
    joinVoiceChannel({
      channelId: voiceChannel.id,
      guildId: voiceChannel.guild.id,
      adapterCreator: voiceChannel.guild.voiceAdapterCreator,
      selfDeaf: false,
    });
  }
});

client.on("speech", (msg) => {
  // If bot didn't recognize speech, content will be empty
  if (!msg.content) return;

  // Send message for processing
  processMessage(msg, msg.author.username);

  // Send message for debugging
  console.log(msg.author.username + ": " + msg.content);
});

client.on("ready", () => {


  console.log("Ready!");
});

async function processMessage(msg, author) {
  // If the last message time was over 10 minutes ago, create a new JSON file.
  if (checkLastMsgTime() == true) {
    createEmptyJSONFile();
  }

  // Read history json into array
  let history = readJSON();

  // Append new message to history array
  history.push({ 'role': 'user', 'content': author + ": " + msg.content });

  // Send history array to OpenAI API
  history = await promptModel(history);

  // Write new history to file.
  writeJSON(history);

  // Pick last message from history array
  let response = `${history[history.length - 1]['role'].trim()}: ${history[history.length - 1]['content'].trim()}`;
                  
  // Prune response of prefixes
  // response = prunePrefix(response);
  console.log(response);

  // Convert response to speech

  // Play response
}

async function promptModel(history) {
  // Send history with new message to OpenAI API
  const completion = await openai.createChatCompletion({
    model: "gpt-3.5-turbo",
    messages: history
  });

  /* Append history with prompt and response. */
  history.push({
    'role': completion.data.choices[0].message.role,
    'content': completion.data.choices[0].message.content
  });

  return history;
}

function checkLastMsgTime() {
  const currentTime = new Date();
  const tenMinutesAgo = new Date(currentTime.getTime() - 10 * 60 * 1000);

  // If the last message time was over 10 minutes ago, return true.
  if (lastMsgTime < tenMinutesAgo) {
    lastMsgTime = currentTime;
    return true;

    // If the last message time was less than 10 minutes ago, return false.
  } else {
    lastMsgTime = currentTime;
    return false;
  }
}

function createEmptyJSONFile() {
  const currentDate = new Date();
  const directory = './history';

  const datePart = currentDate.toISOString().split('T')[0];
  const timePart = currentDate.toISOString().split('T')[1].split('.')[0].replace(/:/g, '');

  const fileName = path.join(directory, `${datePart}_${timePart}.json`);

  const jsonData = {};

  fs.writeFile(fileName, JSON.stringify(jsonData), (err) => {
    if (err) {
      console.error(err);
      return;
    }

    currConvoFile = fileName;
    initializeJSON(config.initialization_prompt);
    console.log(`Empty JSON file "${fileName}" created successfully.`);
  });
}

function readJSON() {
  let rawdata = fs.readFileSync(currConvoFile);
  let array = JSON.parse(rawdata);
  return array;
}

function writeJSON(array) {
  let data = JSON.stringify(array);
  fs.writeFileSync(currConvoFile, data);
}

function wipeJSON() {
  let emptyArray = [];
  let data = JSON.stringify(emptyArray);
  fs.writeFileSync(currConvoFile, data);
}

function initializeJSON(prompt) {
  let initialPrompt = [{ "role": "system", "content": prompt }];
  let data = JSON.stringify(initialPrompt);
  fs.writeFileSync(currConvoFile, data);
}

function prunePrefix(inputStr) {
  let patAssist = /^assistant: /;
  let patName = /^Ash: /;
  let remAssist = inputStr.replace(patAssist, '');
  let remName = remAssist.replace(patName, '');
  return remName;
}

// Create initial JSON file for message history
createEmptyJSONFile();

client.login(config.bot_key);