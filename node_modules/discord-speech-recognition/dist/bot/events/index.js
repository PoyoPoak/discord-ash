"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.setupVoiceJoinEvent = exports.setupSpeechEvent = void 0;
var speech_1 = require("./speech");
Object.defineProperty(exports, "setupSpeechEvent", { enumerable: true, get: function () { return __importDefault(speech_1).default; } });
var voiceJoin_1 = require("./voiceJoin");
Object.defineProperty(exports, "setupVoiceJoinEvent", { enumerable: true, get: function () { return __importDefault(voiceJoin_1).default; } });
//# sourceMappingURL=index.js.map