import {
  CommandManager,
  command,
  monitor,
  Iterator,
  Monitor
} from '../manager.js';
import ModelNotFound from './errors.js';


export class FieldMonitor extends Monitor {

  constructor(mapFn, obj, field) {
    super(obj, 'change:' + field);
    this.mapFn = mapFn;
    this.field = field;
  }

  mapEventResult(model, value) {
    return {
      'value': value
    };
  }


  async monit(partialResult) {
    let self = this;

    function handler(...args) {
      let result = self.mapEventResult(...args);

      if (result) {
        partialResult(result);
      }
    }
    handler(this.obj, this.obj[this.field]);
    this.obj.on(this.evt, handler, this);
    await this.promise;
    this.obj.off(this.evt, handler, this);
    throw new StopMonitor();
  }
}


export class CollectionItemMonitor extends Monitor {
  constructor(mapFn, obj, evt) {
    super(obj, evt);
    this.mapFn = mapFn;
  }

  mapEventResult(item) {
    return {
      'item': this.mapFn(item)
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
  async monitModel() {
    return new CollectionItemMonitor(this.constructor.mapItem, this.model, 'change');
  }

  @monitor
  async monitField({
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
      throw ModelNotFound(`Item with ID "${id}" not found`);
    }
    return item;
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
  async getItemById({
    id
  }) {
    return this.mapItem(this.loadItem(id));
  }

  @monitor
  async monitAdd() {
    return new CollectionItemMonitor((item) => this.mapItem(item), this.collection, 'add');
  }

  @monitor
  async monitRemove() {
    return new CollectionItemMonitor((item) => this.mapItem(item), this.collection, 'remove');
  }

  @monitor
  async monitChange() {
    return new CollectionItemMonitor((item) => this.mapItem(item), this.collection, 'change');
  }

  @command
  async createModelManager({
    id
  }) {
    let model = this.loadItem(id);

    this.addSubmanager(id, this.getModelManagerClass()(model));

    return id;
  }

}