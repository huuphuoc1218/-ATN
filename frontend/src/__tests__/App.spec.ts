import { describe, it, expect } from 'vitest'

import { mount } from '@vue/test-utils'
import App from '../App.vue'

describe('App', () => {
  it('renders router view container', () => {
    const wrapper = mount(App, {
      global: {
        stubs: {
          RouterView: {
            template: '<div data-test="router-view-stub" />',
          },
        },
      },
    })

    expect(wrapper.find('[data-test="router-view-stub"]').exists()).toBe(true)
  })
})
