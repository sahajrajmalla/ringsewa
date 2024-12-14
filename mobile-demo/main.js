import './style.css'
import AgoraRTC from "agora-rtc-sdk-ng"
import AgoraRTM from "agora-rtm-sdk"

import appid from '../appId.js'

const token = null

const rtcUid =  Math.floor(Math.random() * 2032)
const rtmUid =  String(Math.floor(Math.random() * 2032))

const getRoomId = () => {
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);

  if (urlParams.get('room')){
    return urlParams.get('room').toLowerCase()
  }
}

let roomId = getRoomId() || null
document.getElementById('form').roomname.value = roomId

let audioTracks = {
  localAudioTrack: null,
  remoteAudioTracks: {},
};

let micMuted = true

let rtcClient;
let rtmClient;
let channel;

let avatar;

// New variable to manage automated responses
let automatedResponseInterval = null;
const AUTOMATED_RESPONSES_DIR = 'automated-response'; // Directory for MP3 files

// List of available response files
const RESPONSES = [
    '0_intro.wav',
    '1_name.wav',
    '2_price.wav',
    '3_location.wav',
    '4_description.wav',
   
];

// Delays between responses (in milliseconds)
const RESPONSE_DELAYS = [2000,4000, 3000, 6000, 7000];

// Function to play automated responses with variable delays
const startAutomatedResponses = () => {
  console.log('Starting automated responses');
  let responseIndex = 0;
  let delayIndex = 0;

  const playNextResponse = () => {
    if (responseIndex >= RESPONSES.length) return; // Stop if all responses are played

    const randomResponse = RESPONSES[responseIndex]; // Select current response file

    // Create audio element with the correct public folder path
    const audio = new Audio(`/automated-response/${randomResponse}`);

    // When audio ends, wait for the delay before playing the next response
    audio.addEventListener('ended', () => {
        console.log(`Finished playing: ${randomResponse}`);

        // Wait for the delay before playing the next response
        const nextDelay = RESPONSE_DELAYS[delayIndex] || 0;
        delayIndex++;

        // After delay, play the next response
        setTimeout(() => {
            responseIndex++;
            playNextResponse();
        }, nextDelay);
    });

    // Play the current response
    audio.play()
        .then(() => {
            console.log(`Playing: ${randomResponse}`);
        })
        .catch((error) => {
            console.error('Error playing automated response:', error);
            // Continue to next response even if the current one fails to play
            responseIndex++;
            const nextDelay = RESPONSE_DELAYS[delayIndex] || 0;
            delayIndex++;
            setTimeout(() => {
                playNextResponse();
            }, nextDelay);
        });
};


  // Start the first response
  playNextResponse();
};


const initRtm = async (name) => {
  rtmClient = AgoraRTM.createInstance(appid)
  await rtmClient.login({'uid':rtmUid, 'token':token})

  channel = rtmClient.createChannel(roomId)
  await channel.join()

  await rtmClient.addOrUpdateLocalUserAttributes({'name':name, 'userRtcUid':rtcUid.toString(), 'userAvatar':avatar})

  getChannelMembers()

  window.addEventListener('beforeunload', leaveRtmChannel)

  channel.on('MemberJoined', handleMemberJoined)
  channel.on('MemberLeft', handleMemberLeft)
}

const initRtc = async () => {
  rtcClient = AgoraRTC.createClient({ mode: "rtc", codec: "vp8" });

  rtcClient.on("user-published", handleUserPublished)
  rtcClient.on("user-left", handleUserLeft);
  
  await rtcClient.join(appid, roomId, token, rtcUid)
  audioTracks.localAudioTrack = await AgoraRTC.createMicrophoneAudioTrack();
  audioTracks.localAudioTrack.setMuted(micMuted)
  await rtcClient.publish(audioTracks.localAudioTrack)

  // Start automated responses when RTC is initialized
  startAutomatedResponses();

  initVolumeIndicator()
}

let initVolumeIndicator = async () => {
  AgoraRTC.setParameter('AUDIO_VOLUME_INDICATION_INTERVAL', 200);
  rtcClient.enableAudioVolumeIndicator();
  
  rtcClient.on("volume-indicator", volumes => {
    volumes.forEach((volume) => {
      console.log(`UID ${volume.uid} Level ${volume.level}`);

      try{
          let item = document.getElementsByClassName(`avatar-${volume.uid}`)[0]

         if (volume.level >= 50){
           item.style.borderColor = '#00ff00'
         }else{
           item.style.borderColor = "#fff"
         }
      }catch(error){
        console.error(error)
      }
    });
  })
}

let handleUserPublished = async (user, mediaType) => {
  await rtcClient.subscribe(user, mediaType);

  if (mediaType == "audio"){
    audioTracks.remoteAudioTracks[user.uid] = [user.audioTrack]
    user.audioTrack.play();
  }
}

let handleUserLeft = async (user) => {
  delete audioTracks.remoteAudioTracks[user.uid]
}

let handleMemberJoined = async (MemberId) => {
  let {name, userRtcUid, userAvatar} = await rtmClient.getUserAttributesByKeys(MemberId, ['name', 'userRtcUid', 'userAvatar'])

  let newMember = `
  <div class="speaker user-rtc-${userRtcUid}" id="${MemberId}">
    <img class="user-avatar avatar-${userRtcUid}" src="${userAvatar}"/>
      <p>${name}</p>
  </div>`

  document.getElementById("members").insertAdjacentHTML('beforeend', newMember)
}

let handleMemberLeft = async (MemberId) => {
  document.getElementById(MemberId).remove()
}

let getChannelMembers = async () => {
  let members = await channel.getMembers()

  for (let i = 0; members.length > i; i++){
    let {name, userRtcUid, userAvatar} = await rtmClient.getUserAttributesByKeys(members[i], ['name', 'userRtcUid', 'userAvatar'])

    let newMember = `
    <div class="speaker user-rtc-${userRtcUid}" id="${members[i]}">
        <img class="user-avatar avatar-${userRtcUid}" src="${userAvatar}"/>
        <p>${name}</p>
    </div>`
  
    document.getElementById("members").insertAdjacentHTML('beforeend', newMember)
  }
}

const toggleMic = async (e) => {
  if (micMuted){
    e.target.src = 'icons/mic.svg'
    e.target.style.backgroundColor = 'ivory'
    micMuted = false
  }else{
    e.target.src = 'icons/mic-off.svg'
    e.target.style.backgroundColor = 'indianred'
    
    micMuted = true
  }
  audioTracks.localAudioTrack.setMuted(micMuted)
}

let lobbyForm = document.getElementById('form')

const enterRoom = async (e) => {
  e.preventDefault()

  roomId = e.target.roomname.value.toLowerCase();
  window.history.replaceState(null, null, `?room=${roomId}`);

  initRtc()

  let displayName = e.target.displayname.value;
  initRtm(displayName)

  lobbyForm.style.display = 'none'
  document.getElementById('room-header').style.display = "flex"
  document.getElementById('room-name').innerText = roomId
}

let leaveRtmChannel = async () => {
  await channel.leave()
  await rtmClient.logout()
}

let leaveRoom = async () => {
  // Stop automated responses (if needed, though the function above 
  // will naturally stop after exhausting delays)
  if (automatedResponseInterval) {
    clearInterval(automatedResponseInterval);
    automatedResponseInterval = null;
  }

  audioTracks.localAudioTrack.stop()
  audioTracks.localAudioTrack.close()
  rtcClient.unpublish()
  rtcClient.leave()

  leaveRtmChannel()

  document.getElementById('form').style.display = 'block'
  document.getElementById('room-header').style.display = 'none'
  document.getElementById('members').innerHTML = ''
}
lobbyForm.addEventListener('submit', enterRoom)
document.getElementById('leave-icon').addEventListener('click', leaveRoom)
document.getElementById('mic-icon').addEventListener('click', toggleMic)