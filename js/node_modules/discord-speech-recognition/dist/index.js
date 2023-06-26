"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.resolveSpeechWithWitai = exports.resolveSpeechWithGoogleSpeechV2 = exports.voiceJoin = exports.speech = exports.VoiceMessage = exports.addSpeechEvent = void 0;
var addSpeechEvent_1 = require("./bot/addSpeechEvent");
Object.defineProperty(exports, "addSpeechEvent", { enumerable: true, get: function () { return addSpeechEvent_1.addSpeechEvent; } });
var voiceMessage_1 = require("./bot/voiceMessage");
Object.defineProperty(exports, "VoiceMessage", { enumerable: true, get: function () { return __importDefault(voiceMessage_1).default; } });
var events_1 = require("./events");
Object.defineProperty(exports, "speech", { enumerable: true, get: function () { return events_1.speech; } });
Object.defineProperty(exports, "voiceJoin", { enumerable: true, get: function () { return events_1.voiceJoin; } });
var googleV2_1 = require("./speechRecognition/googleV2");
Object.defineProperty(exports, "resolveSpeechWithGoogleSpeechV2", { enumerable: true, get: function () { return googleV2_1.resolveSpeechWithGoogleSpeechV2; } });
var witai_1 = require("./speechRecognition/witai");
Object.defineProperty(exports, "resolveSpeechWithWitai", { enumerable: true, get: function () { return witai_1.resolveSpeechWithWitai; } });
//# sourceMappingURL=index.js.map