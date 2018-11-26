import {
  ConnManager
} from './conn.js';
import {
  StreamManager
} from './stream.js';
import {
  ChatCollectionManager
} from './chat.js';
import {
  MessageCollectionManager
} from './message.js';
import {
  MessageInfoCollectionManager
} from './messageInfo.js';
import {
  ContactCollectionManager
} from './contact.js';
import {
  GroupMetadataCollectionManager
} from './groupMetadata.js';
import {
  WapManager
} from './wap.js';
import {
  UIControllerManager
} from './uiController.js';
import {
  StorageManager
} from './storage.js';
import {
  StickerPackCollectionManager
} from './stickerPack.js';
import {
  PresenceCollectionManager
} from './presence.js';
import {
  ProfilePicThumbCollectionManager
} from './profilePicThumb.js';
import {
  StatusCollectionManager
} from './status.js';


function getArtifactsDefs() {
  return {
    'conn': (module) => module.default && typeof module.default == "object" && 'ref' in module.default && 'refTTL' in module.default ? module.default : null,
    'store': (module) => module.Chat && module.Msg ? module : null,
    'wap': (module) => module.queryExist ? module : null,
    'stream': (module) => module.default && typeof module.default == "object" && 'stream' in module.default && 'socket' in module.default ? module.default : null,
    'uiController': (module) => module.default && module.default.focusNextChat ? module.default : null,
    'mediaCollectionClass': (module) => (module.prototype && module.prototype.processFiles !== undefined) || (module.default && module.default.prototype && module.default.prototype.processFiles !== undefined) ? module.default ? module.default : module : null,
    'createPeerForContact': (module) => (module.default && module.default.prototype && module.default.prototype.isServer && module.default.prototype.isUser) ? module.default : null,
  }
}

function getRequirementsDefs() {
  return {
    'connManager': {
      'requirements': ['conn'],
      'build': function(mainManager, artifacts) {
        let manager = new ConnManager(artifacts['conn']);
        mainManager.addSubmanager('conn', manager);
        return manager;
      }
    },
    'chatManager': {
      'requirements': ['store', 'mediaCollectionClass', 'createPeerForContact'],
      'build': function(mainManager, artifacts) {
        let manager = new ChatCollectionManager(
          artifacts['store'].Chat,
          artifacts['mediaCollectionClass'],
          artifacts['createPeerForContact']
        );
        mainManager.addSubmanager('chats', manager);
        return manager;
      }
    },
    'messageManager': {
      'requirements': ['store'],
      'build': function(mainManager, artifacts) {
        let manager = new MessageCollectionManager(
          artifacts['store'].Msg
        );
        mainManager.addSubmanager('messages', manager);
        return manager;
      }
    },
    'messageInfoManager': {
      'requirements': ['store'],
      'build': function(mainManager, artifacts) {
        let manager = new MessageInfoCollectionManager(
          artifacts['store'].MsgInfo
        );
        mainManager.addSubmanager('messageInfos', manager);
        return manager;
      }
    },
    'contactManager': {
      'requirements': ['store'],
      'build': function(mainManager, artifacts) {
        let manager = new ContactCollectionManager(artifacts['store'].Contact);
        mainManager.addSubmanager('contacts', manager);
        return manager;
      }
    },
    'groupMetadataManager': {
      'requirements': ['store'],
      'build': function(mainManager, artifacts) {
        let manager = new GroupMetadataCollectionManager(artifacts['store'].GroupMetadata);
        mainManager.addSubmanager('groupMetadata', manager);
        return manager;
      }
    },
    'wapManager': {
      'requirements': ['wap'],
      'build': function(mainManager, artifacts) {
        let manager = new WapManager(artifacts['wap']);
        mainManager.addSubmanager('wap', manager);
        return manager;
      }
    },
    'streamManager': {
      'requirements': ['stream'],
      'build': function(mainManager, artifacts) {
        let manager = new StreamManager(artifacts['stream']);
        mainManager.addSubmanager('stream', manager);
        return manager;
      }
    },
    'uiControllerManager': {
      'requirements': ['uiController'],
      'build': function(mainManager, artifacts) {
        let manager = new UIControllerManager(artifacts['uiController']);
        mainManager.addSubmanager('uiController', manager);
        return manager;
      }
    },
    'storageManager': {
      'build': function(mainManager) {
        let manager = new StorageManager();
        mainManager.addSubmanager('storage', manager);
        return manager;
      }
    },
    'stickerManager': {
      'requirements': ['store'],
      'build': function(mainManager, artifacts) {
        let manager = new StickerPackCollectionManager(
          artifacts['store'].StickerPack
        );
        mainManager.addSubmanager('stickerPacks', manager);
        return manager;
      }
    },
    'presenceManager': {
      'requirements': ['store'],
      'build': function(mainManager, artifacts) {
        let manager = new PresenceCollectionManager(
          artifacts['store'].Presence
        );
        mainManager.addSubmanager('presences', manager);
        return manager;
      }
    },
    'profilePicThumbManager': {
      'requirements': ['store'],
      'build': function(mainManager, artifacts) {
        let manager = new ProfilePicThumbCollectionManager(
          artifacts['store'].ProfilePicThumb
        );
        mainManager.addSubmanager('profilePicThumbs', manager);
        return manager;
      }
    },
    'statusManager': {
      'requirements': ['store'],
      'build': function(mainManager, artifacts) {
        let manager = new StatusCollectionManager(
          artifacts['store'].Status
        );
        mainManager.addSubmanager('status', manager);
        return manager;
      }
    }
  };
}

export default function createManagers(mainManager) {
  function discoveryModules(modules) {
    var artifactsDefs = getArtifactsDefs();
    var requirementsDefs = getRequirementsDefs();

    var artifacts = {}

    function checkRequiements() {
      let recheck = true;

      while (recheck) {
        recheck = false;
        for (let reqIdx in requirementsDefs) {
          let req = requirementsDefs[reqIdx];
          let canBuild = true;

          (req.requirements || []).forEach(function(item) {
            if (!(item in artifacts)) {
              canBuild = false;
            }
          })

          if (canBuild) {
            artifacts[reqIdx] = req.build(mainManager, artifacts);
            delete requirementsDefs[reqIdx];
            recheck = true;
            console.log("Built requirement: " + reqIdx);
          }
        }
      }
    }


    function checkArtifacts(module) {
      for (let art in artifactsDefs) {
        let artifact = artifactsDefs[art](module);
        if (artifact) {
          artifacts[art] = artifact;
          console.log("Got artifact: " + art);
          return true;
        }
      }
    }

    for (let idx in modules) {
      if ((typeof modules[idx] === "object") && modules[idx]) {
        let first = Object.values(modules[idx])[0];
        if ((typeof first === "object") && (first.exports)) {
          for (let idx2 in modules[idx]) {
            let module = modules(idx2);

            if (!module) {
              continue;
            }

            if (checkArtifacts(module)) {
              checkRequiements();
            }

            if ((artifactsDefs.length == 0) || (requirementsDefs.length == 0)) {
              return;
            }
          }
        }
      }
    }
  }

  webpackJsonp([], {
    'whalesong': (x, y, z) => discoveryModules(z)
  }, 'whalesong');
}