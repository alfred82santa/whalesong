import {
  command
} from '../manager.js';
import {
  CollectionManager,
  ModelManager
} from './common.js';

export class ContactManager extends ModelManager {

  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      formattedName: item.formattedName,
      isHighLevelVerified: item.isHighLevelVerified,
      isMe: item.isMe,
      isMyContact: item.isMyContact,
      isPSA: item.isPSA,
      isUser: item.isUser,
      isVerified: item.isVerified,
      isWAContact: item.isWAContact,
      profilePicThumbObj: item.profilePicThumb ? item.profilePicThumb.toJSON() : {},
      statusMute: item.statusMute,
      userhash: item.userhash,
      userid: item.userid
    });
  }
}

export class ContactCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return ContactManager;
  }

  constructor(collection, conn) {
    super(collection);
    this.conn = conn;
  }

  @command
  async resyncContacts() {
    return this.collection.resyncContacts();
  }

  @command
  async getMe() {
    return this.mapItem(await this.collection.find(this.conn.me));
  }
}