import {IBackMsg, FloatArray, WidgetState, WidgetStates} from 'autogen/proto'

/**
 * Manages widget values, and sends widget update messages back to the server.
 */
export class WidgetStateManager {
  // Called to deliver a message to the server
  private readonly sendBackMsg: (msg: IBackMsg) => void
  private readonly widgetStates: Map<string, WidgetState> = new Map<string, WidgetState>()

  public constructor(sendBackMsg: (msg: IBackMsg) => void) {
    this.sendBackMsg = sendBackMsg
  }

  /**
   * True if our widget state dict is empty. This will be the case only when the browser
   * initially connects to the server for the first time.
   */
  public get isEmpty(): boolean {
    return this.widgetStates.size === 0
  }

  /**
   * Sets the trigger value for the given widget ID to true, sends an updateWidgets message
   * to the server, and then immediately unsets the trigger value.
   */
  public setTriggerValue(widgetId: string): void {
    this.getOrCreateWidgetStateProto(widgetId).triggerValue = true
    this.sendUpdateWidgetsMessage()
    this.deleteWidgetStateProto(widgetId)
  }

  public getBoolValue(widgetId: string): boolean | undefined {
    const state = this.getWidgetStateProto(widgetId)
    if (state != null && state.value === 'boolValue') {
      return state.boolValue
    }

    return undefined
  }

  public setBoolValue(widgetId: string, value: boolean): void {
    this.getOrCreateWidgetStateProto(widgetId).boolValue = value
    this.sendUpdateWidgetsMessage()
  }

  public getIntValue(widgetId: string): number | undefined {
    const state = this.getWidgetStateProto(widgetId)
    if (state != null && state.value === 'intValue') {
      return state.intValue
    }

    return undefined
  }

  public setIntValue(widgetId: string, value: number): void {
    this.getOrCreateWidgetStateProto(widgetId).intValue = value
    this.sendUpdateWidgetsMessage()
  }

  public getFloatValue(widgetId: string): number | undefined {
    const state = this.getWidgetStateProto(widgetId)
    if (state != null && state.value === 'floatValue') {
      return state.floatValue
    }

    return undefined
  }

  public setFloatValue(widgetId: string, value: number): void {
    this.getOrCreateWidgetStateProto(widgetId).floatValue = value
    this.sendUpdateWidgetsMessage()
  }

  public getStringValue(widgetId: string): string | undefined {
    const state = this.getWidgetStateProto(widgetId)
    if (state != null && state.value === 'stringValue') {
      return state.stringValue
    }

    return undefined
  }

  public setStringValue(widgetId: string, value: string): void {
    this.getOrCreateWidgetStateProto(widgetId).stringValue = value
    this.sendUpdateWidgetsMessage()
  }

  public getFloatArrayValue(widgetId: string): number[] | undefined {
    const state = this.getWidgetStateProto(widgetId)
    if (state != null &&
        state.value === 'floatArrayValue' &&
        state.floatArrayValue != null &&
        state.floatArrayValue.value != null) {

      return state.floatArrayValue.value
    }

    return undefined
  }

  public setFloatArrayValue(widgetId: string, value: number[]): void {
    this.getOrCreateWidgetStateProto(widgetId).floatArrayValue = FloatArray.fromObject({ value })
    this.sendUpdateWidgetsMessage()
  }

  public sendUpdateWidgetsMessage(): void {
    this.sendBackMsg({ updateWidgets: this.createWigetStatesMsg() })
  }

  private createWigetStatesMsg(): WidgetStates {
    const msg = new WidgetStates()
    this.widgetStates.forEach(value => msg.widgets.push(value))
    return msg
  }

  /**
   * Returns the WidgetState proto for the widget with the given ID.
   * If no such WidgetState exists yet, one will be created.
   */
  private getOrCreateWidgetStateProto(id: string): WidgetState {
    let state = this.getWidgetStateProto(id)
    if (state == null) {
      state = new WidgetState({ id })
      this.widgetStates.set(id, state)
    }
    return state
  }

  /**
   * Removes the WidgetState proto with the given id, if it exists
   */
  private deleteWidgetStateProto(id: string): void {
    this.widgetStates.delete(id)
  }

  private getWidgetStateProto(id: string): WidgetState | undefined {
    return this.widgetStates.get(id)
  }
}
