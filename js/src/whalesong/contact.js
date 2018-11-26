import {
  command
} from '../manager.js';
import {
  CollectionManager,
  ModelManager
} from './common.js';
import {
  ProfilePicThumbManager
} from './profilePicThumb.js';
import {
  StatusManager
} from './status.js';

export class ContactManager extends ModelManager {

  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      id: item.id._serialized,
      formattedName: item.formattedName,
      isHighLevelVerified: item.isHighLevelVerified,
      isMe: item.isMe,
      isMyContact: item.isMyContact,
      isPSA: item.isPSA,
      isUser: item.isUser,
      isVerified: item.isVerified,
      isWAContact: item.isWAContact,
      profilePicThumbObj: item.profilePicThumb ? ProfilePicThumbManager.mapModel(item.profilePicThumb) : null,
      statusMute: item.statusMute,
      userhash: item.userhash,
      userid: item.userid,
      status: item.status ? StatusManager.mapModel(item.status) : null
    });
  }

  constructor(model) {
    super(model);

    if (model.profilePicThumb) {
      this.addSubmanager(
        'profilePicThumb',
        manager.getSubmanager('profilePicThumbs').getSubmanager(
          this.model.id._serialized
        )
      );
    }
  }

  @command
  async block() {
    return this.model.setBlock(true);
  }

  @command
  async unblock() {
    return this.model.setBlock(false);
  }
}

export class ContactCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return ContactManager;
  }

  @command
  async resyncContacts() {
    return this.collection.resyncContacts();
  }

  @command
  async getMe() {
    return this.mapItem(await this.collection.find(manager.getSubmanager('conn').me));
  }
}