function selectChoices(selector) {
  document.querySelectorAll(selector).forEach(element => {
    const usersChoices = new Choices(element, {
      removeItemButton: true,
      duplicateItems: false,
      searchFloor: 4,
      searchResultLimit: 7
    })
    document.querySelector('.choices input').addEventListener('keyup', event => {
      event.preventDefault()
      /* Reset choices when first new caracters are typed. */
      usersChoices.setChoices([], 'id', 'name', true)
      /* Intercept -return- it's capture by 'click' for adding users */
      if (event.keyCode === 38) return
      if (event.target.value.length < 3) return
      request(`/en/profile/suggest/?terms=${event.target.value}`)
        .catch(console.error.bind(console))
        .then(users => usersChoices.setChoices(users, 'id', 'name', true))
    })
  })
}

window.addEventListener('load', () => {
  selectChoices('#authors')
  selectChoices('#translators')
})
