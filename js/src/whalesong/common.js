import {
  CommandManager,
  command,
  monitor,
  Iterator,
  Monitor
} from '../manager.js';
import {
  ModelNotFound
} from './errors.js';


export class BaseFieldMonitor extends Monitor {

  constructor(obj, field, mapFn) {
    super(obj, 'change:' + field, mapFn);
    this.field = field;
  }

  mapEventResult(...args) {
    if (this.mapFn) {
      return this.mapFn(...args);
    }
    return {
      'value': args[1]
    };
  }
}

export class FieldMonitor extends BaseFieldMonitor {

  initMonitor(partialResult) {
    this.handler(partialResult, this.obj, this.obj[this.field]);
  }
}


export class CollectionItemMonitor extends Monitor {

  mapEventResult(...args) {
    let item = this.mapFn(args[0]);
    if (!item) {
      return null;
    }
    return {
      'item': item
    };
  }
}

export class CollectionItemFieldMonitor extends BaseFieldMonitor {

  mapEventResult(...args) {
    return {
      'value': args[1],
      'itemId': this.mapFn(args[0]).id
    };
  }
}

export class ModelManager extends CommandManager {

  constructor(model) {
    super();
    this.model = model;
  }

  static mapModel(item) {
    return item.toJSON();
  }

  @command
  async getModel() {
    return this.constructor.mapModel(this.model);
  }

  @monitor
  async monitorModel() {
    return new CollectionItemMonitor(this.model, 'change', (item) => this.constructor.mapModel(item));
  }

  @monitor
  async monitorField({
    field
  }) {
    return new FieldMonitor(this.model, field);
  }
}

export class CollectionManager extends CommandManager {

  static getModelManagerClass() {
    return ModelManager;
  }

  constructor(collection) {
    super();
    this.collection = collection;
  }

  mapItem(item) {
    return this.constructor.getModelManagerClass().mapModel(item);
  }

  loadItem(id) {
    let item = this.collection.get(id);
    if (!item) {
      throw new ModelNotFound(`Item with ID "${id}" not found`);
    }
    return item;
  }

  async findItem(id) {
    let item = this.collection.find(id);
    if (!item) {
      throw new ModelNotFound(`Item with ID "${id}" not found`);
    }
    return item;
  }

  getSubmanager(name) {
    try {
      return super.getSubmanager(name);
    } catch (err) {
      try {
        return new(this.constructor.getModelManagerClass())(this.loadItem(name));
      } catch (err2) {
        throw err;
      }
    }
  }

  @command
  async getItems() {
    return new Iterator(
      (partialResult) => this.collection.forEach(
        (item) => partialResult(
          this.mapItem(item)
        )
      )
    );
  }

  @command
  async getLength() {
    return this.collection.length;
  }

  @command
  async getItemById({
    id
  }) {
    return this.mapItem(this.loadItem(id));
  }

  @command
  async findItemById({
    id
  }) {
    return this.mapItem(await this.findItem(id));
  }

  @command
  async removeItemById({
    id
  }) {
    this.collection.remove(this.loadItem(id));
  }

  @command
  async getFirst() {
    return this.mapItem(this.collection.models[0]);
  }

  @command
  async getLast() {
    return this.mapItem(this.collection.last());
  }

  @monitor
  async monitorAdd() {
    return new CollectionItemMonitor(this.collection, 'add', (item) => this.mapItem(item));
  }

  @monitor
  async monitorRemove() {
    return new CollectionItemMonitor(this.collection, 'remove', (item) => this.mapItem(item));
  }

  @monitor
  async monitorChange() {
    return new CollectionItemMonitor(this.collection, 'change', (item) => this.mapItem(item));
  }

  @monitor
  async monitorField({
    field
  }) {
    return new CollectionItemFieldMonitor(this.collection, field, (item) => this.mapItem(item));
  }
}