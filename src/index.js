const { Configuration, OpenAIApi } = require("openai");
const { Client, GatewayIntentBits } = require("discord.js");
const { addSpeechEvent } = require("discord-speech-recognition");
const textToSpeech = require('@google-cloud/text-to-speech');
const { joinVoiceChannel, createAudioResource, createAudioPlayer, VoiceConnectionStatus } = require("@discordjs/voice");
const fs = require('fs');
const path = require('path');
const config = require('../config.json');
const util = require('util');

process.env.GOOGLE_APPLICATION_CREDENTIALS = './gcloud.json';

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

const ttsClient = new textToSpeech.TextToSpeechClient();
const openai = new OpenAIApi(configuration);
const player = createAudioPlayer();

addSpeechEvent(client);
let lastMsgTime;
let currConvoFile;
let gptModel = 'gpt-3.5-turbo';

client.on("messageCreate", async (msg) => {
  const voiceChannel = msg.member?.voice.channel;
  if (voiceChannel) {
    try {
      const connection = joinVoiceChannel({
        channelId: voiceChannel.id,
        guildId: voiceChannel.guild.id,
        adapterCreator: voiceChannel.guild.voiceAdapterCreator,
        selfDeaf: false,
      });

      connection.on(VoiceConnectionStatus.Ready, () => {
        console.log('The connection has entered the Ready state - ready to play audio!');
        console.log(`Connected to voice channel with ID: ${connection.joinConfig.channelId}`); // Prints the channel ID
        const subscription = connection.subscribe(player);

        if (subscription) {
          console.log('Player subscribed successfully!');
        } else {
          console.log('Failed to subscribe player!');
        }
      });
    } catch (error) {
      console.error('Error connecting to voice channel:', error);
    }
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

  // Delete old mp3 file if it exists.
  deleteMp3();

  // Command 99 to clear history.
  if(msg.content == 'Execute Order 99') {
    createEmptyJSONFile();
    console.log("INVOKED ORDER 99");
  }

  if(msg.content == 'Execute Order 77') {
    gptModel = 'gpt-4'
    console.log("INVOKED ORDER 77");
  }

  if(msg.content == 'Execute Order 66') {
    gptModel = 'gpt-3.5-turbo'
    console.log("INVOKED ORDER 66");
  }

  if(msg.content == 'Execute Order 55') {
    process.exit(0);
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
  response = prunePrefix(response);
  console.log("Ash: " + response);

  // Generate mp3 file from response.
  await tts(response);

  // Play response
  const resource = createAudioResource('output.mp3');
  player.play(resource);
}

async function promptModel(history) {
  // Send history with new message to OpenAI API
  const completion = await openai.createChatCompletion({
    model: gptModel,
    messages: history
  });

  /* Append history with prompt and response. */
  history.push({
    'role': completion.data.choices[0].message.role,
    'content': completion.data.choices[0].message.content
  });

  return history;
}

async function tts(inputStr) {
  // Construct the request
  const request = {
    input: { text: inputStr },
    // Select the language and SSML voice gender (optional)
    voice: { languageCode: 'en-US', ssmlGender: 'FEMALE', name: 'en-US-Studio-O' },
    // select the type of audio encoding
    audioConfig: { audioEncoding: 'MP3' },
  };

  // Performs the text-to-speech request
  const [response] = await ttsClient.synthesizeSpeech(request);
  // Write the binary audio content to a local file
  const writeFile = util.promisify(fs.writeFile);
  await writeFile('output.mp3', response.audioContent, 'binary');
  // console.log('Audio content written to file: output.mp3');
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
    console.log(`"${fileName}" created successfully.`);
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

function deleteMp3() {
  const filePath = './output.mp3';

  if (fs.existsSync(filePath)) {
    fs.unlink(filePath, (err) => {
      if (err) {
        console.error(err);
        return;
      }

      // console.log(`Deleted ${filePath} successfully.`);
    });
  } else {
    console.log(`${filePath} does not exist.`);
  }
}

// Create initial JSON file for message history
createEmptyJSONFile();

client.login(config.bot_key);