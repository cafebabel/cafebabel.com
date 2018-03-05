const target = document.querySelector('#authors-complete')

const awesomplete = new Awesomplete(target, {
  filter(text, input) {
    return Awesomplete.FILTER_CONTAINS(text, input.match(/[^,]*$/)[0])
  },

  item(text, input) {
    return Awesomplete.ITEM(text, input.match(/[^,]*$/)[0])
  },

  replace(text) {
    const before = this.input.value.match(/^.+,\s*|/)[0]
    this.input.value = `${before} ${text.label}, `
  }
})

window.addEventListener('load', () => {
  target.addEventListener('keyup', event => {
    event.preventDefault()
    /* Intercept -return- it's capture by 'click' for adding users */
    if (event.keyCode === 38) return
    let submission = event.target.value
    submission = submission
      .split(',')
      .pop()
      .trim()
    if (submission.length < 3) return
    request(`/en/profile/suggest/?terms=${submission}`)
      .catch(console.error.bind(console))
      .then(users => {
        awesomplete.list = users.map(user => [user.name, user.pk])
      })
  })
  target.addEventListener('awesomplete-selectcomplete', event => {
    console.log(event)
    const authors = document.querySelector('#authors')
    authors.value = authors.value
      ? `${authors.value},${event.text.value}`
      : event.text.value
  })
})
