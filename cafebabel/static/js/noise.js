/* tv noise effect https://codepen.io/eugene-bulkin/pen/zEgyH */
const canvas = document.querySelector('.noise')
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
    })()
}
