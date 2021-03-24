function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min) + min); //The maximum is exclusive and the minimum is inclusive
}

function interpolateColor(color1, color2, factor) {
    if (!factor) factor = 0.5;
    var result = color1.slice();
    for (var i = 0; i < 3; i++) {
        result[i] = Math.round(result[i] + factor*(color2[i] - color1[i]));
    }
    return result;
};

function perlin_noise(canvas, colorPair, factorBounds) {
    var canvas_ctx = canvas.getContext('2d');
    var offscreen = document.createElement('canvas');
    var offscreen_ctx = offscreen.getContext('2d');
    var saved_alpha = canvas_ctx.globalAlpha;

    /* Fill the offscreen buffer with random noise. */
    offscreen.width = canvas.width;
    offscreen.height = canvas.height;

    var offscreen_id = offscreen_ctx.getImageData(
        0, 0,
        offscreen.width, offscreen.height
    );
    var offscreen_pixels = offscreen_id.data;

    for (var i = 0; i < offscreen_pixels.length; i += 4) {
        var color = interpolateColor(
            colorPair[0],
            colorPair[1],
            (factorBounds[1] - factorBounds[0])*Math.random() + factorBounds[0]
        );
        offscreen_pixels[i    ] = color[0];
        offscreen_pixels[i + 1] = color[1];
        offscreen_pixels[i + 2] = color[2];
        offscreen_pixels[i + 3] = 255;
    }

    offscreen_ctx.putImageData(offscreen_id, 0, 0);

    /* Scale random iterations onto the canvas to generate Perlin noise. */
    for (var size = 4; size <= offscreen.width; size *= 2) {
        var x = Math.floor(Math.random()*   (offscreen.width - size));
        var y = Math.floor(Math.random()*(offscreen.height - size));

        canvas_ctx.globalAlpha = 4/size;
        canvas_ctx.drawImage(
            offscreen,
            x, y,
            size, size,
            0, 0,
            canvas.width, canvas.height
        );
    }

    canvas_ctx.globalAlpha = saved_alpha;
}