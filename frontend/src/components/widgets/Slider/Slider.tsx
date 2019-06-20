/**
 * @license
 * Copyright 2019 Streamlit Inc. All rights reserved.
 */

import React from 'react'
// @ts-ignore
import { Slider as UISlider } from 'baseui/slider';
import { Map as ImmutableMap } from 'immutable'
import { WidgetStateManager } from 'lib/WidgetStateManager'
import { PureStreamlitElement, StState } from 'components/shared/StreamlitElement/'
import './Slider.scss'

interface Props {
  element: ImmutableMap<string, any>;
  widgetMgr: WidgetStateManager;
  width: number;
}

interface State extends StState {
  value: number[];
}

class Slider extends PureStreamlitElement<Props, State> {
  public constructor(props: Props) {
    super(props)

    const widgetId = this.props.element.get('id')
    const value = this.props.element.get('value').toArray()

    this.state = { value }
    this.props.widgetMgr.setFloatArrayValue(widgetId, value)
    this.props.widgetMgr.sendUpdateWidgetsMessage()
  }

  private handleChange = (e: any) => {
    const widgetId = this.props.element.get('id')
    const value = e.value

    this.setState({ value })
    this.props.widgetMgr.setFloatArrayValue(widgetId, value)
    this.props.widgetMgr.sendUpdateWidgetsMessage()
  }

  public safeRender(): React.ReactNode {
    const label = this.props.element.get('label')
    const min = this.props.element.get('min')
    const max = this.props.element.get('max')
    const step = this.props.element.get('step')
    const style = { width: this.props.width }

    return (
      <div className="Widget stSlider" style={style}>
        <p className="label">{label}: {this.state.value.join(" ")}</p>
        <UISlider
          min={min}
          max={max}
          step={step}
          value={this.state.value}
          onChange={this.handleChange}
        />
      </div>
    )
  }
}

export default Slider
