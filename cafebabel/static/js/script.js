/* Preloader fadeout when page is loaded */
const preloader = document.querySelector('#preloader')
preloader.classList.add('fadeout')
setTimeout(() => {
  preloader.classList.add('hidden')
}, 300)

/* open menu */
Array.from(document.querySelectorAll('button.menu')).forEach((button) => {
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
  if (a.href.search(/\w+:\/\//) === 0 && a.hostname !== location.hostname) a.setAttribute('target', '_blank')
})

/* animation flash info */
const flashes = document.querySelector('.flashes')
if (flashes) {
  setTimeout(() => {
    flashes.classList.add('hidden')
  }, 3000)
}

/* display profile social network field on click */
const socialIcons = Array.from(document.querySelectorAll('.edit .social-networks li'))
if (socialIcons) {
  socialIcons.forEach(socialIcon => {
    socialIcon.querySelector('a').addEventListener('click', (event) => {
      event.preventDefault()
      const socialsClick = socialIcon.querySelector('a').contains(event.target)
      if (socialsClick) {
        socialIcons.forEach((li) => li.classList.remove('active'))
        socialIcon.classList.add('active')
        socialIcon.querySelector('input').focus()
      } else {
        socialIcon.classList.remove('active')
      }
    })
  })
}

function activateInput (input) {
  if (!input) return
  const parent = input.parentElement
  parent.classList.add('active', 'completed')
}

function deactivateInput (input) {
  const parent = input.parentElement
  parent.classList.remove('active', 'completed')
}

/* Detect chrome autofill https://stackoverflow.com/questions/35049555/chrome-autofill-autocomplete-no-value-for-password/40852860#40852860  */
const autofillContent = `"${String.fromCharCode(0xFEFF)}"`
function checkAutofill (input) {
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
Array.from(document.querySelectorAll('.authentication-form > div > input')).forEach(input => {
  input.value && activateInput(input)
  input.addEventListener('change', () => activateInput(input))
  input.addEventListener('focus', () => activateInput(input))
  input.addEventListener('blur', () => input.value || deactivateInput(input))
})

/* animation title field create article */
Array.from(document.querySelectorAll('h1.edit input')).forEach(inputh1 => {
  const h1 = inputh1.parentElement
  inputh1.addEventListener('focus', () => h1.classList.add('active'))
  inputh1.addEventListener('blur', () => inputh1.value || h1.classList.remove('active'))
})

/* highlight file upload area on hover or dragenter */
function addListenerMulti (element, events, fn) {
  events.split(' ').forEach(event => element.addEventListener(event, fn, false)) /* https://stackoverflow.com/questions/8796988/binding-multiple-events-to-a-listener-without-jquery */
}
const articleFileInput = document.querySelector('.create-article-page .file input')
const dropArea = document.querySelector('canvas')
if (articleFileInput) {
  addListenerMulti(articleFileInput, 'dragenter focus click', () => {
    dropArea.classList.add('active')
  })
  addListenerMulti(articleFileInput, 'dragleave blur drop', () => {
    dropArea.classList.remove('active')
  })
  articleFileInput.addEventListener('change', () => {
    document.querySelector('.file label').innerHTML(' ')
  })
}

/* display picture file name after selection on profile edit https://tympanus.net/codrops/2015/09/15/styling-customizing-file-inputs-smart-way/ */
const profileFileInput = document.querySelector('.profile-page.edit .file input')
const profileLabel = document.querySelector('.profile-page.edit .file output')
const sizeInfo = profileFileInput.parentElement.querySelector('small')
profileFileInput && profileFileInput.addEventListener('change', (event) => {
  const image = event.target.files[0]
  const fileName = image.name
  const reader = new FileReader()
  reader.readAsDataURL(image)
  reader.addEventListener('loadend', (event) => {
    profileLabel.innerHTML = `
      <figure>
      <img src=${reader.result} alt="Preview of your profile picture">
      <figcaption>${fileName}</figcaption>
      </figure>
    `
    sizeInfo.classList.toggle('oversized', Math.round(reader.result.length / 1024) > 500)
  })
})
