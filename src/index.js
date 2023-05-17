const { Configuration, OpenAIApi } = require("openai");
const { Client, GatewayIntentBits } = require("discord.js");
const { joinVoiceChannel } = require("@discordjs/voice");
const { addSpeechEvent } = require("discord-speech-recognition");
const fs = require('fs');
const path = require('path');


const client = new Client({
  intents: [
        GatewayIntentBits.GuildVoiceStates,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.Guilds,
        GatewayIntentBits.MessageContent,
      ],
});

const configuration = new Configuration({
  apiKey: "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",
});

addSpeechEvent(client);
const openai = new OpenAIApi(configuration);
let lastMsgTime;

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

  // Send message to OpenAI API
  // getCompletion();

  // Send message for debugging
  console.log(msg.author.username + ": " + msg.content);
});

client.on("ready", () => {
  console.log("Ready!");
});

async function processMessage(message) {
  if (checkLastMsgTime() == true) {
    createEmptyJSONFile();
  }

  // Append to message history json file

  // Read history json into array

  // Send history + message to OpenAI API

  // Prune response

  // Convert response to speech

  // Play response
}

async function getCompletion(gptModel, prompt) {
  const completion = await openai.createChatCompletion({
    model: gptModel,
    messages: [{
      role: "user", 
      content: prompt}],
  });
  console.log(completion.data.choices[0].message);
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

    console.log(`Empty JSON file "${fileName}" created successfully.`);
  });
}

// createEmptyJSONFile();

client.login("MTA3MDI3ODcyNzU4MzQxMjI0NA.GlBtF0.jWFtm5zflGh4hn6yn4Tu-mY10tbGDftFwq9yJ0");