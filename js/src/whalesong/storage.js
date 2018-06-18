import {
  command,
  monitor,
  CommandManager,
  Monitor
} from '../manager.js';


export class StorageMonitor extends Monitor {

  mapEventResult(evt) {
    return {};
  }

  async monit(partialResult) {
    let self = this;

    function handler(evt) {
      let result = self.mapEventResult(evt);
      partialResult(result);
    }
    window.addEventListener('storageChange', handler);
    await this.promise;
    window.removeEventListener('storageChange', handler);
    throw new StopMonitor();
  }
}

export class StorageItemMonitor extends Monitor {

  mapEventResult(evt) {
    return {
      'key': evt.detail.key,
      'newValue': evt.detail.newValue,
      'oldValue': evt.detail.oldValue
    };
  }

  async monit(partialResult) {
    let self = this;

    function handler(evt) {
      let result = self.mapEventResult(evt);
      partialResult(result);
    }
    window.addEventListener('storageSet', handler);
    window.addEventListener('storageRemove', handler);
    await this.promise;
    window.removeEventListener('storageSet', handler);
    window.removeEventListener('storageRemove', handler);
    throw new StopMonitor();
  }
}

export class StorageManager extends CommandManager {

  initStorageEvents() {
    if (this._eventInitiated) {
      return
    }

    let originalSetItem = Storage.prototype.setItem;
    let originalRemoveItem = Storage.prototype.removeItem;
    let originalClear = Storage.prototype.clear;

    Storage.prototype.setItem = function() {
      window.dispatchEvent(new CustomEvent('storageSet', {
        'detail': {
          'key': arguments[0],
          'newValue': arguments[1],
          'oldValue': window.localStorage.getItem(arguments[0])
        }
      }));

      window.dispatchEvent(new Event('storageChange'));
      originalSetItem.apply(this, arguments);
    }

    Storage.prototype.removeItem = function() {
      window.dispatchEvent(new CustomEvent('storageRemove', {
        'detail': {
          'key': arguments[0],
          'oldValue': window.localStorage.getItem(arguments[0]),
          'newValue': null
        }
      }));

      window.dispatchEvent(new Event('storageChange'));
      originalRemoveItem.apply(this, arguments);
    }

    Storage.prototype.clear = function() {
      window.dispatchEvent(new Event('storageChange'));
      originalClear.apply(this, arguments);
    }

    this._eventInitiated = true;
  }

  @command
  async getStorage() {
    return window.localStorage;
  }

  @command
  async getItem({
    key
  }) {
    return window.localStorage.get(key);
  }

  @command
  async setItem({
    key,
    value
  }) {
    return window.localStorage.set(key, value);
  }

  @command
  async setStorage({
    data
  }) {
    for (let key in data) {
      await this.setItem({
        key: key,
        value: data[key]
      });
    }
  }

  @monitor
  async monitStorage() {
    this.initStorageEvents();
    return new StorageMonitor();
  }

  @monitor
  async monitItemStorage() {
    this.initStorageEvents();
    return new StorageItemMonitor();
  }
}