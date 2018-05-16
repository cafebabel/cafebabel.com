/* Preloader fadeout when page is loaded */
const preloader = document.querySelector('#preloader-layer')
preloader.classList.add('fadeout')
setTimeout(() => {
  preloader.classList.add('hidden')
}, 300)

/* open menu */
Array.from(document.querySelectorAll('button.menu')).forEach(button => {
  button.addEventListener('click', () => {
    const activeButton = document.querySelector('button.active.menu')
    if (activeButton) {
      activeButton.classList.remove('active')
      if (activeButton !== button) {
        button.classList.add('active')
      }
    } else {
      button.classList.add('active')
    }
  })
})

/* external link in new tab */
Array.from(document.querySelectorAll('a')).forEach(a => {
  if (a.href.search(/\w+:\/\//) === 0 && a.hostname !== location.hostname)
    a.setAttribute('target', '_blank')
})

/* smooth scroll to anchor https://stackoverflow.com/a/17733311/6481285 */
function animate(elem, style, from, to, time) {
  if (!elem) return
  const start = new Date().getTime()
  const timer = setInterval(() => {
    const step = Math.min(1, (new Date().getTime() - start) / time)
    elem[style] = from + step * (to - from)
    if (step === 1) {
      clearInterval(timer)
    }
  }, 25) /* allow smooth scroll on firefox */
  elem[style] = from
}
const subscribeLink = document.querySelector(
  '#social-networks .icon-newsletter2'
)
subscribeLink.addEventListener('click', event => {
  const target = document.querySelector(event.target.getAttribute('href'))
  const scrollPosition =
    window.pageYOffset !== undefined
      ? window.pageYOffset
      : (document.documentElement || document.body.parentNode || document.body)
          .scrollTop
  animate(
    document.scrollingElement || document.documentElement,
    'scrollTop',
    scrollPosition,
    target.offsetTop,
    300 /* Total duration of the animation in ms */
  )
})

/* animation flash info */
const flashes = document.querySelector('.flashes')
if (flashes) {
  setTimeout(() => {
    flashes.classList.add('hidden')
  }, 3000)
}

/* display profile social network field on click */
const socialIcons = Array.from(
  document.querySelectorAll('.profile-page .social-networks li')
)
if (socialIcons) {
  socialIcons.forEach(socialIcon => {
    socialIcon.querySelector('a').addEventListener('click', event => {
      event.preventDefault()
      const socialsClick = socialIcon.querySelector('a').contains(event.target)
      if (socialsClick) {
        socialIcons.forEach(li => li.classList.remove('active'))
        socialIcon.classList.add('active')
        socialIcon.querySelector('input').focus()
      } else {
        socialIcon.classList.remove('active')
      }
    })
  })
  // when input element loses the focus the target become inactive
  socialIcons.forEach(socialIcon => {
    socialIcon.querySelector('input').addEventListener('focusout', event => {
      socialIcon.classList.remove('active')
    })
  })
}

function activateInput(input) {
  if (!input) return
  const parent = input.parentElement
  parent.classList.add('active', 'completed')
}

function deactivateInput(input) {
  const parent = input.parentElement
  parent.classList.remove('active', 'completed')
}

/* Detect chrome autofill https://stackoverflow.com/questions/35049555/chrome-autofill-autocomplete-no-value-for-password/40852860#40852860  */
const autofillContent = `"${String.fromCharCode(0xfeff)}"` // Keep semicolon for jsmin.
function checkAutofill(input) {
  if (input && !input.value) {
    const style = window.getComputedStyle(input)
    if (style.content !== autofillContent) {
      return false
    }
  }
  activateInput(input)
  return true
}
const input = document.querySelector('input[type=password]')
if (!checkAutofill(input)) {
  deactivateInput(input)
  let interval = 0
  const intervalId = setInterval(() => {
    if (checkAutofill(input) || interval++ >= 20) {
      activateInput(input)
      clearInterval(intervalId)
    }
  }, 100)
}
/* animation login fields */
Array.from(
  document.querySelectorAll('.authentication-form > div > input')
).forEach(input => {
  input.value && activateInput(input)
  input.addEventListener('change', () => activateInput(input))
  input.addEventListener('focus', () => activateInput(input))
  input.addEventListener('blur', () => input.value || deactivateInput(input))
})

/* animation title field create article */
Array.from(document.querySelectorAll('h1.edit input')).forEach(inputh1 => {
  const h1 = inputh1.parentElement
  inputh1.addEventListener('focus', () => h1.classList.add('active'))
  inputh1.addEventListener(
    'blur',
    () => inputh1.value || h1.classList.remove('active')
  )
})
