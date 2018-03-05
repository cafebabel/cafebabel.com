window.addEventListener('load', () => {
  const target = document.querySelector('#authors')
  const authorsChoices = new Choices(target, {
    removeItemButton: true
  })
  document.querySelector('.choices input').addEventListener('keyup', event => {
    event.preventDefault()
    /* Intercept -return- it's capture by 'click' for adding users */
    if (event.keyCode === 38) return
    if (event.target.value.length < 3) return
    request(`/en/profile/suggest/?terms=${event.target.value}`)
      .catch(console.error.bind(console))
      .then(users => authorsChoices.setChoices(users, 'pk', 'name', true))
  })
})
