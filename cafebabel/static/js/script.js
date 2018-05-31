/* Preloader slide down when input:submit is clicked */
const inputSubmit = document.querySelector('input[type="submit"]')
if (inputSubmit) {
  inputSubmit.addEventListener('click', () => {
    preloader.classList.remove('slideup')
    preloader.classList.remove('hidden')
    preloader.classList.add('slidedown')
  })
}

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
const newsletterLink = document.querySelector('.icon-newsletter2')
newsletterLink.addEventListener('click', () => {
  const activeButton = document.querySelector('button.active.menu')
  activeButton.classList.remove('active')
})

/* external link in new tab */
Array.from(document.querySelectorAll('a')).forEach(a => {
  if (a.href.search(/\w+:\/\//) === 0 && a.hostname !== location.hostname)
    a.setAttribute('target', '_blank')
})

/* NOT smooth scroll to anchor https://stackoverflow.com/a/17733311/6481285 */
const subscribeLink = document.querySelector(
  '#social-networks .icon-newsletter2'
)
const subscribeLinkHome = document.querySelector(
  '.participation-newseletter-form a'
)
if (subscribeLinkHome) {
  subscribeLinkHome.addEventListener('click', event => {
    event.preventDefault()
    window.scrollTo(0, document.querySelector('#content').scrollHeight)
  })
}

subscribeLink.addEventListener('click', event => {
  event.preventDefault()
  window.scrollTo(0, document.querySelector('#content').scrollHeight)
})

/* Hover effect article image */
const articleThumbnails = document.querySelectorAll('.home article')
articleThumbnails.forEach(articleThumbnail => {
  const articleThumbnailLinks = articleThumbnail.querySelectorAll('a')
  articleThumbnailLinks.forEach(articleThumbnailLink => {
    articleThumbnailLink.addEventListener('mouseover', () => {
      articleThumbnail.classList.add('thumbnail-hover')
    })
    articleThumbnailLink.addEventListener('mouseout', () => {
      articleThumbnail.classList.remove('thumbnail-hover')
    })
  })
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

/* animation picto sections */
const viewportHeight = Math.max(
  document.documentElement.clientHeight,
  window.innerHeight || 0
) /* https://stackoverflow.com/a/8876069/6481285 */
Array.from(document.querySelectorAll('.svg-animation')).forEach(svg => {
  window.addEventListener('scroll', () => {
    if (svg.getBoundingClientRect().top < viewportHeight) {
      svg.classList.add('active')
      window.onscroll = null
    }
  })

/* Add player if tag #video is present */
Array.from(
  document.querySelectorAll('article .article-detail .tags-list a.tag-video')
).forEach(homepageTagList => {
  homepageTagList.parentNode.parentNode.parentNode.classList.add(
    'article-video'
  )

})
