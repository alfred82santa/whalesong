import { command } from "../manager";
import { CollectionManager, ModelManager } from "./common";

export class StatusV3Manager extends ModelManager {
  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      id: item.id._serialized,
      contact: item.contact ? ContactManager.mapModel(item.contact) : null,
      msgs: null,
      expireTs: item.expireTs,
      hasUnread: item.hasUnread,
      lastReceivedKey: item.lastReceivedKey ? item.lastReceivedKey._serialized : null,
      totalCount: item.totalCount,
      unreadCount: item.unreadCount,
      readKeys: item.readKeys
    });
  }

  /*
  {
    fromMe: false
    id: "AFC0FBE1007851F741B0024EAB0F32E8"
    remote: {
      server: "broadcast"
      user: "status"
      _serialized: "status@broadcast"
    }
    _serialized: "false_status@broadcast_AFC0FBE1007851F741B0024EAB0F32E8"
  }, {
    server: "c.us"
    user: "553496562348"
    _serialized: "553496562348@c.us"
  }
  */
  @command
  async sendReadStatus({
    readMessage,
    fromUser,
  }) {
    return await this.model.sendReadStatus(readMessage, fromUser);
  }

  @command
  async loadMore() {
    return this.model.loadMore();
  }
}

export class StatusV3CollectionManager extends CollectionManager {
  @command
  async getStatus({
    unread
  }) {
    return await this.collection.getUnexpired(unread);
  }

  @command
  async sync() {
    return this.collection.sync();
  }

  @command
  async getMyStatus() {
    return this.collection.getMyStatus();
  }
}