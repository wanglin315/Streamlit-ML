/**
 * @license
 * Copyright 2019 Streamlit Inc. All rights reserved.
 */

import React from 'react'
import { TimePicker as UITimePicker } from 'baseui/datepicker'
import { Map as ImmutableMap } from 'immutable'
import { WidgetStateManager } from 'lib/WidgetStateManager'

interface Props {
  disabled: boolean;
  element: ImmutableMap<string, any>;
  widgetMgr: WidgetStateManager;
  width: number;
}

interface State {
  /**
   * The value specified by the user via the UI. If the user didn't touch this
   * widget's UI, it's undefined.
   */
  value?: string;
}

class TimeInput extends React.PureComponent<Props, State> {
  public state: State = {}

  /**
   * Return the user-entered value, or the widget's default value
   * if the user hasn't interacted with it yet.
   */
  private get valueOrDefault(): Date {
    if (this.state.value === undefined) {
      return stringToDate(this.props.element.get('value') as string)
    } else {
      return stringToDate(this.state.value)
    }
  }

  private handleChange = (newDate: Date): void => {
    const widgetId = this.props.element.get('id')

    const value = dateToString(newDate)
    this.setState({ value })
    this.props.widgetMgr.setStringValue(widgetId, value)
  }

  public render(): React.ReactNode {
    const label = this.props.element.get('label')
    const style = { width: this.props.width }

    const selectOverride = {
      Select: {
        props: {
          disabled: this.props.disabled,
        },
      },
    }

    return (
      <div className="Widget stTimeInput" style={style}>
        <label>{label}</label>
        <UITimePicker
          format="24"
          value={this.valueOrDefault}
          onChange={this.handleChange}
          overrides={selectOverride}
        />
      </div>
    )
  }
}

function stringToDate(value: string): Date {
  const [hours, minutes] = value.split(':').map(Number)
  const date = new Date()
  date.setHours(hours)
  date.setMinutes(minutes)
  return date
}

function dateToString(value: Date): string {
  const hours = value.getHours().toString().padStart(2, '0')
  const minutes = value.getMinutes().toString().padStart(2, '0')
  return hours + ':' + minutes
}

export default TimeInput
