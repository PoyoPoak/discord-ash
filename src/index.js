// Import the required packages
const {
  Client,
  Events,
  GatewayIntentBits,
} = require("discord.js");

const {
  joinVoiceChannel,
  createAudioResource,
  AudioPlayerStatus,
  createAudioPlayer,
  StreamType,
  entersState,
  VoiceConnectionStatus,
  createAudioReceiver,
} = require('@discordjs/voice');

const { token, googleCredentials } = require('../config.json');
const { StreamOpusDecoder } = require('@discordjs/opus');
const { SpeechClient } = require('@google-cloud/speech');

const speechClient = new SpeechClient();

process.env.GOOGLE_APPLICATION_CREDENTIALS = googleCredentials;

// Add required intents
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildVoiceStates,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildEmojisAndStickers,
    GatewayIntentBits.GuildIntegrations,
    GatewayIntentBits.GuildVoiceStates,
    GatewayIntentBits.GuildPresences,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildMessageReactions,
  ]
});

// Listen for 'messageCreate' event to check for the '!join' command
client.on('messageCreate', async (message) => {
  if (message.content === '!join') {
    // Voice channel checks
    if (!message.member.voice.channel) {
      return message.reply('Please join a voice channel first!');
    } else if ((message.member.voice.channel.members.filter((e) => client.user.id === e.user.id).size > 0)) {
      return message.reply(`I'm already in your voice channel!`);
    } else if (!message.member.voice.channel.joinable) {
      return message.reply(`I don't have permission to join that voice channel!`);
    } else if (!message.member.voice.channel.speakable) {
      return message.reply(`I don't have permission to speak in that voice channel!`);
    }

    // If user is in a voice channel, join
    if (message.member.voice.channel) {
      // Join the user's voice channel
      const connection = joinVoiceChannel({
        channelId: message.member.voice.channel.id,
        guildId: message.guild.id,
        adapterCreator: message.guild.voiceAdapterCreator,
        selfDeaf: false,
      });

      // Log connection debug information
      connection.on('debug', console.debug);

      // Create a voice receiver
      connection.receiver.speaking.on('start', async (userId) => {
        const audioStream = connection.receiver.subscribe(userId, { mode: 'opus' });

        // Configure the streaming recognition request
        const request = {
          config: {
            encoding: 'OGG_OPUS',
            sampleRateHertz: 48000,
            languageCode: 'en-US',
          },
          interimResults: true,
        };

        // Create a recognize stream and pipe the audio stream into it
        const recognizeStream = speechClient.streamingRecognize(request)
          .on('error', console.error)
          .on('data', data => {
            const transcription = data.results
              .map(result => result.alternatives[0].transcript)
              .join('\n');
            console.log(`Transcription: ${transcription}`);
          });

        audioStream.pipe(recognizeStream);
      });
    }
  }
});


// Bot ready sequence
client.once(Events.ClientReady, c => {
  console.log(`Logged in as ${c.user.tag}`);
});

client.login(token);