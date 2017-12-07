/* Preloader fadeout when page is loaded */
var preloader = document.querySelector('#preloader')
preloader.classList.add('fadeout')
setTimeout(() => {
    preloader.classList.add('hidden')
}, 300)

/* open menu */
const menuButton = document.querySelector('button.menu-button')
menuButton.addEventListener('click', () => {
    menuButton.classList.toggle('active')
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
const socialIcons = Array.from(document.querySelectorAll('.social-networks li'))
if (socialIcons) {
    socialIcons.forEach(socialIcon => {
        socialIcon.querySelector('a').addEventListener('click', (event) => {
            event.preventDefault()
            const SocialsClick = socialIcon.querySelector('a').contains(event.target)
            if (SocialsClick) {
                socialIcons.forEach((li) => li.classList.remove('active'))
                socialIcon.classList.add('active')
                socialIcon.querySelector('input').focus()
            } else {
                socialIcon.classList.remove('active')
            }
        })
    })
}

/* animation login fields */
Array.from(document.querySelectorAll('.authentication-form > div > input')).forEach(input => {
    const parent = input.parentElement
    input.addEventListener('change', () => {
        parent.classList.add('active', 'completed')
    })
    input.addEventListener('focus', () => {
        parent.classList.add('active', 'completed')
    })
    input.addEventListener('blur', () => {
        if (input.value) return
        parent.classList.remove('active', 'completed')
    })
})

/* highlight file upload area on hover or dragenter */
function addListenerMulti(element, events, fn) {
    events.split(' ').forEach(event => element.addEventListener(event, fn, false)) /* https://stackoverflow.com/questions/8796988/binding-multiple-events-to-a-listener-without-jquery */
}
const fileInput = document.querySelector('.file input')
const dropArea = document.querySelector('canvas')
if (fileInput) {
    addListenerMulti(fileInput, 'dragenter focus click', () => {
        dropArea.classList.add('active')
    })
    addListenerMulti(fileInput, 'dragleave blur drop', () => {
        dropArea.classList.remove('active')
    })
    fileInput.addEventListener('change', () => {
        document.querySelector('.file label').innerHTML(' ')
    })
}

/* tv noise effect https://codepen.io/eugene-bulkin/pen/zEgyH how to know how "heavy" is it? */
const canvas = document.querySelector('canvas')
if (canvas) {
    const context = canvas.getContext('2d')

    function resize() {
        canvas.width = window.innerWidth
        canvas.height = window.innerHeight
    }
    resize();
    window.onresize = resize

    function noise(context) {
        var w = context.canvas.width,
            h = context.canvas.height,
            idata = context.createImageData(w, h),
            buffer32 = new Uint32Array(idata.data.buffer),
            len = buffer32.length,
            i = 0
        for(; i < len;)
            buffer32[i++] = ((50 * Math.random())|0) << 24
        context.putImageData(idata, 0, 0)
    }
    var toggle = true;
    (function loop() {
        toggle = !toggle
        if (toggle) {
            requestAnimationFrame(loop)
            return
        }
        noise(context)
        requestAnimationFrame(loop)
    })();
}