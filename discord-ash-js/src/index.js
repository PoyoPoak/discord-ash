// Require the necessary discord.js classes
const { Client, Events, GatewayIntentBits } = require('discord.js');
const { joinVoiceChannel } = require('@discordjs/voice');
const { token } = require('../config.json');

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
      });

      // Log connection debug information
      connection.on('debug', console.debug);
    }
  }
});


// Bot ready sequence
client.once(Events.ClientReady, c => {
  console.log(`Logged in as ${c.user.tag}`);
});

client.login(token);