<template>
    <canvas ref="posterCanvas" class="poster-canvas"></canvas>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const posterCanvas = ref(null);

const prepareCanvas = () => {
    const canvas = posterCanvas.value;
    if (!canvas) return null;

    const ratio = window.devicePixelRatio || 1;
    canvas.width = 540 * ratio;
    canvas.height = 1200 * ratio;
    canvas.style.width = '540px';
    canvas.style.height = '1200px';

    const ctx = canvas.getContext('2d');
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    return ctx;
};

const getPrimaryName = (anime) => {
    if (!anime) return '';
    if (anime.names?.length) {
        const primary = anime.names.find((item) => !!item);
        if (primary) return primary;
    }
    return anime.name || '';
};

const drawPost = (nickname, avatar, positiveList, negativeList, options = { download: true }) => {
    const ctx = prepareCanvas();
    if (!ctx) return;

    function drawLine(x1, y1, x2, y2) {
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 1;

        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);

        ctx.stroke();
    };

    function drawRoundRect(x, y, width, height, radius, gradient) {
        ctx.beginPath();
        ctx.moveTo(x + radius, y);

        ctx.lineTo(x + width - radius, y);
        ctx.arcTo(x + width, y, x + width, y + height, radius);

        ctx.lineTo(x + width, y + height - radius);
        ctx.arcTo(x + width, y + height, x + width - width, y + height, radius);

        ctx.lineTo(x + radius, y + height);
        ctx.arcTo(x, y + height, x, y + height - radius, radius);

        ctx.lineTo(x, y + radius);
        ctx.arcTo(x, y, x + radius, y, radius);

        ctx.closePath();

        ctx.fillStyle = gradient;
        ctx.fill();
    }

    function drawWrappedText(ctx, text, x, y, maxWidth, lineHeight) {
        const words = text.split('');
        let line = '';
        const lines = [];

        for (let n = 0; n < words.length; n++) {
            const testLine = line + words[n];
            const testWidth = ctx.measureText(testLine).width;

            if (testWidth > maxWidth && n > 0) {
                lines.push(line);
                line = words[n];
            } else {
                line = testLine;
            }
        }
        lines.push(line);

        for (let i = 0; i < lines.length; i++) {
            const lineWidth = ctx.measureText(lines[i]).width;
            const centeredX = x - lineWidth / 2;
            ctx.fillText(lines[i], centeredX, y + i * lineHeight);
        }
    }

    function drawWrappedTextBottomLeft(ctx, text, x, y, maxWidth, lineHeight) {
        const words = text.split('');
        let line = '';
        const lines = [];

        for (let n = 0; n < words.length; n++) {
            const testLine = line + words[n];
            const testWidth = ctx.measureText(testLine).width;

            if (testWidth > maxWidth && n > 0) {
                lines.push(line);
                line = words[n];
            } else {
                line = testLine;
            }
        }
        lines.push(line);

        const initialY = y - (lines.length - 1) * lineHeight;

        for (let i = 0; i < lines.length; i++) {
            const lineWidth = ctx.measureText(lines[i]).width;
            const centeredX = x - lineWidth / 2;
            ctx.fillText(lines[i], centeredX, initialY + i * lineHeight);
        }
    }

    function splitTextByWidth(ctx, text, maxWidth) {
        const chars = text.split('');
        const lines = [];
        let line = '';

        chars.forEach((char) => {
            const testLine = line + char;
            if (ctx.measureText(testLine).width > maxWidth && line) {
                lines.push(line);
                line = char;
            } else {
                line = testLine;
            }
        });

        if (line) lines.push(line);
        return lines;
    }

    function layoutNameLines(text, maxWidth, maxHeight) {
        const minFontSize = 6;
        const maxLines = Math.max(1, Math.floor(maxHeight / minFontSize));

        for (let lineCount = 1; lineCount <= maxLines; lineCount++) {
            let fontSize = maxHeight / lineCount;
            ctx.font = `lighter ${fontSize}px Alibaba-PuHuiTi`;
            let lines = splitTextByWidth(ctx, text, maxWidth);
            const nextLineThreshold = lineCount < maxLines ? maxHeight / (lineCount + 1) : minFontSize;

            while ((lines.length > lineCount || fontSize * lineCount > maxHeight) && fontSize > nextLineThreshold) {
                fontSize -= 1;
                ctx.font = `lighter ${fontSize}px Alibaba-PuHuiTi`;
                lines = splitTextByWidth(ctx, text, maxWidth);
            }

            ctx.font = `lighter ${fontSize}px Alibaba-PuHuiTi`;
            lines = splitTextByWidth(ctx, text, maxWidth);

            if (lines.length <= lineCount && fontSize * lines.length <= maxHeight) {
                // If the font has already shrunk past the next line's share, prefer trying more lines.
                if (fontSize < nextLineThreshold && lineCount < maxLines) {
                    continue;
                }
                return { fontSize, lines };
            }
        }

        const finalFontSize = Math.max(minFontSize, maxHeight / maxLines);
        ctx.font = `lighter ${finalFontSize}px Alibaba-PuHuiTi`;
        return { fontSize: finalFontSize, lines: splitTextByWidth(ctx, text, maxWidth) };
    }

    function loadImage(src, { retry = 0 } = {}) {
        return new Promise((resolve, reject) => {
            const img = new Image();

            // 是否需要跨域（只对外链头像开启）
            if (/^https?:\/\//.test(src)) {
                img.crossOrigin = 'anonymous';
            }

            img.onload = () => resolve(img);

            img.onerror = () => {
                console.error(`[loadImage Error] 加载失败: ${src}`);

                if (retry > 0) {
                    console.warn(`[loadImage] 正在重试(${retry}) → ${src}`);
                    // 递归重试
                    loadImage(src, { retry: retry - 1 })
                        .then(resolve)
                        .catch(reject);
                    return;
                }

                // 最终失败，返回包含 src 的错误对象
                reject(new Error(`无法加载图片: ${src}`));
            };

            img.src = src;
        });
    }

    const EMPTY_IMAGE =
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIW2NkYGBgAAAABQABDQottAAAAABJRU5ErkJggg==";

    const getPosterSrc = (anime) => {
        if (!anime || !anime.id || anime.id === 0) {
            return EMPTY_IMAGE;   // 返回透明图
        }

        return `/posters/${anime.id}.jpg`;
    };

    const getAvatarSrc = (src) => {
        if (src === "/avatar.jpg") {
            return src
        }

        return `https://top3.bgmss.fun/proxy?url=${src}`
    }

    function drawRadiusImg(x, y, width, height, radius, img) {
        ctx.save();
        ctx.beginPath();
        ctx.moveTo(x + radius, y);
        ctx.arcTo(x + width, y, x + width, y + height, radius);
        ctx.arcTo(x + width, y + height, x, y + height, radius);
        ctx.arcTo(x, y + height, x, y, radius);
        ctx.arcTo(x, y, x + width, y, radius);
        ctx.closePath();
        ctx.clip();
        ctx.drawImage(img, x, y, width, height);
        ctx.restore();
    }

    Promise.all([
        loadImage(getAvatarSrc(avatar)),
        loadImage('/positive.png'),
        loadImage('/negative.png'),
        loadImage(getPosterSrc(positiveList[1])),
        loadImage(getPosterSrc(positiveList[0])),
        loadImage(getPosterSrc(positiveList[2])),
        loadImage(getPosterSrc(negativeList[1])),
        loadImage(getPosterSrc(negativeList[2])),
        loadImage(getPosterSrc(negativeList[0])),
    ]).then(([avatarImg, bgmBzdImg, bgm38Img, p1, p2, p3, n1, n2, n3]) => {
        ctx.clearRect(0, 0, 540, 1200);

        const linearBg = ctx.createLinearGradient(0, 0, 0, 1200);
        linearBg.addColorStop(0, "#0f0f1a");
        linearBg.addColorStop(0.35, "#131324");
        linearBg.addColorStop(1, "#0c0c12");

        ctx.fillStyle = linearBg;
        ctx.fillRect(0, 0, 540, 1200);

        const radialBg = ctx.createRadialGradient(270, 0, 0, 270, 0, 1080);
        radialBg.addColorStop(0, "rgba(205, 81, 147, 0.235)");
        radialBg.addColorStop(0.4, "rgba(205, 81, 147, 0)");
        radialBg.addColorStop(1, "rgba(0, 0, 0, 0)");

        ctx.fillStyle = radialBg;
        ctx.fillRect(0, 0, 540, 1200);

        ctx.fillStyle = '#ffffff';

        const userName = nickname;
        const maxNameHeight = 65;
        const maxNameWidth = 340;
        const { fontSize: nameFontSize, lines: nameLines } = layoutNameLines(userName, maxNameWidth, maxNameHeight);
        ctx.font = `lighter ${nameFontSize}px Alibaba-PuHuiTi`;
        const nameLineHeight = nameFontSize;
        const titleBaseline = 135; // fixed title y-position
        const nameToTitleGap = 50; // keep original visual gap
        const nameStartY = titleBaseline - nameToTitleGap - (nameLines.length - 1) * nameLineHeight;
        nameLines.forEach((line, index) => {
            ctx.fillText(line, 30, nameStartY + index * nameLineHeight);
        });

        ctx.font = 'lighter 27px Alibaba-PuHuiTi';
        const titleDescription = "的 2025 个人年度新番 Top3";
        ctx.fillText(titleDescription, 30, 135);

        ctx.font = 'lighter 20px Alibaba-PuHuiTi';
        drawWrappedText(ctx, 'top3.bgmss.fun', 270, 1150, 1200, 100);
        drawWrappedText(ctx, '选出你的 2025 年度新番 Top3', 270, 1180, 1200, 100);

        drawLine(27, 168, 510, 168);
        drawLine(27, 1115, 510, 1115);

        ctx.font = 'lighter 40px Alibaba-PuHuiTi';
        const positiveTop3 = "正向 Top3";
        ctx.fillText(positiveTop3, 25, 225);

        const negativeTop3 = "反向 Top3";
        ctx.fillText(negativeTop3, 328, 1078);


        const positiveTop1Gradient = ctx.createLinearGradient(194, 264, 194, 264 + 388);
        positiveTop1Gradient.addColorStop(0, 'rgba(255, 216, 112, 1)');
        positiveTop1Gradient.addColorStop(0.5, 'rgba(96, 84, 69, 0.1)');
        positiveTop1Gradient.addColorStop(1, 'rgba(85, 63, 77, 0.0)');
        drawRoundRect(194, 264, 148, 388, 10, positiveTop1Gradient);

        const positiveTop2Gradient = ctx.createLinearGradient(27, 307, 27, 307 + 388);
        positiveTop2Gradient.addColorStop(0, 'rgba(175, 175, 175, 1)');
        positiveTop2Gradient.addColorStop(0.5, 'rgba(90, 90, 90, 0.1)');
        positiveTop2Gradient.addColorStop(1, 'rgba(85, 63, 77, 0.0)');
        drawRoundRect(27, 307, 148, 388, 10, positiveTop2Gradient);

        const positiveTop3Gradient = ctx.createLinearGradient(363, 307, 363, 307 + 388);
        positiveTop3Gradient.addColorStop(0, 'rgba(126, 92, 53, 1)');
        positiveTop3Gradient.addColorStop(0.5, 'rgba(81, 65, 59, 0.1)');
        positiveTop3Gradient.addColorStop(1, 'rgba(85, 63, 77, 0.0)');
        drawRoundRect(363, 307, 148, 388, 10, positiveTop3Gradient);

        const negativeTop1Gradient = ctx.createLinearGradient(194, 623, 194, 623 + 388);
        negativeTop1Gradient.addColorStop(1, 'rgba(255, 216, 112, 1)');
        negativeTop1Gradient.addColorStop(0.5, 'rgba(113, 87, 98, 0.1)');
        negativeTop1Gradient.addColorStop(0, 'rgba(85, 63, 77, 0.0)');
        drawRoundRect(194, 623, 148, 388, 10, negativeTop1Gradient);

        const negativeTop2Gradient = ctx.createLinearGradient(363, 582, 363, 582 + 388);
        negativeTop2Gradient.addColorStop(1, 'rgba(175, 175, 175, 1)');
        negativeTop2Gradient.addColorStop(0.5, 'rgba(90, 90, 90, 0.1)');
        negativeTop2Gradient.addColorStop(0, 'rgba(85, 63, 77, 0.0)');
        drawRoundRect(363, 582, 148, 388, 10, negativeTop2Gradient);

        const negativeTop3Gradient = ctx.createLinearGradient(27, 582, 27, 582 + 388);
        negativeTop3Gradient.addColorStop(1, 'rgba(126, 92, 53, 1)');
        negativeTop3Gradient.addColorStop(0.5, 'rgba(81, 65, 59, 0.1)');
        negativeTop3Gradient.addColorStop(0, 'rgba(85, 63, 77, 0.0)');
        drawRoundRect(27, 582, 148, 388, 10, negativeTop3Gradient);


        const positiveTop1TextGradient = ctx.createLinearGradient(255, 280, 255, 313);
        positiveTop1TextGradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        positiveTop1TextGradient.addColorStop(1, 'rgba(227, 196, 114, 1)');
        ctx.font = 'lighter 45px Alibaba-PuHuiTi';
        ctx.fillStyle = positiveTop1TextGradient;
        ctx.fillText('1', 256, 310);

        const positiveTop2TextGradient = ctx.createLinearGradient(90, 321, 90, 356);
        positiveTop2TextGradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        positiveTop2TextGradient.addColorStop(1, 'rgba(200, 198, 200, 1)');
        ctx.font = 'lighter 45px Alibaba-PuHuiTi';
        ctx.fillStyle = positiveTop2TextGradient;
        ctx.fillText('2', 90, 356);

        const positiveTop3TextGradient = ctx.createLinearGradient(425, 321, 425, 356);
        positiveTop3TextGradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        positiveTop3TextGradient.addColorStop(1, 'rgba(204, 154, 105, 1)');
        ctx.font = 'lighter 45px Alibaba-PuHuiTi';
        ctx.fillStyle = positiveTop3TextGradient;
        ctx.fillText('3', 425, 356);

        const negativeTop1TextGradient = ctx.createLinearGradient(255, 988, 255, 954);
        negativeTop1TextGradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        negativeTop1TextGradient.addColorStop(1, 'rgba(227, 196, 114, 1)');
        ctx.font = 'lighter 45px Alibaba-PuHuiTi';
        ctx.fillStyle = negativeTop1TextGradient;
        ctx.fillText('1', 260, 988);

        const negativeTop2TextGradient = ctx.createLinearGradient(425, 947, 425, 912);
        negativeTop2TextGradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        negativeTop2TextGradient.addColorStop(1, 'rgba(200, 198, 200, 1)');
        ctx.font = 'lighter 45px Alibaba-PuHuiTi';
        ctx.fillStyle = negativeTop2TextGradient;
        ctx.fillText('2', 425, 947);

        const negativeTop3TextGradient = ctx.createLinearGradient(90, 947, 90, 912);
        negativeTop3TextGradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        negativeTop3TextGradient.addColorStop(1, 'rgba(204, 154, 105, 1)');
        ctx.font = 'lighter 45px Alibaba-PuHuiTi';
        ctx.fillStyle = negativeTop3TextGradient;
        ctx.fillText('3', 90, 947);


        ctx.fillStyle = '#ffffff';
        ctx.font = 'lighter 18px Alibaba-PuHuiTi';

        const positiveTop1Name = getPrimaryName(positiveList[1]);
        drawWrappedText(ctx, positiveTop1Name, 268, 532, 130, 25);
        const positiveTop2Name = getPrimaryName(positiveList[0]);
        drawWrappedText(ctx, positiveTop2Name, 102, 576, 130, 25);
        const positiveTop3Name = getPrimaryName(positiveList[2]);
        drawWrappedText(ctx, positiveTop3Name, 440, 576, 130, 25);

        const negativeTop1Name = getPrimaryName(negativeList[1]);
        drawWrappedTextBottomLeft(ctx, negativeTop1Name, 268, 748, 130, 25);
        const negativeTop2Name = getPrimaryName(negativeList[2]);
        drawWrappedTextBottomLeft(ctx, negativeTop2Name, 102, 705, 130, 25);
        const negativeTop3Name = getPrimaryName(negativeList[0]);
        drawWrappedTextBottomLeft(ctx, negativeTop3Name, 440, 705, 130, 25);


        drawRadiusImg(390, 25, 120, 120, 15, avatarImg);
        ctx.drawImage(bgmBzdImg, 218, 188, 40, 40);
        ctx.drawImage(bgm38Img, 275, 1040, 40, 40);
        drawRadiusImg(206, 326, 124, 175, 8, p1);
        drawRadiusImg(39, 370, 124, 175, 8, p2);
        drawRadiusImg(375, 370, 124, 175, 8, p3);
        drawRadiusImg(206, 763, 124, 175, 8, n1);
        drawRadiusImg(39, 722, 124, 175, 8, n2);
        drawRadiusImg(375, 722, 124, 175, 8, n3);

        function dataURItoBlob(dataURI) {
            const byteString = atob(dataURI.split(',')[1]);
            const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
            const ab = new ArrayBuffer(byteString.length);
            const ia = new Uint8Array(ab);
            for (let i = 0; i < byteString.length; i++) {
                ia[i] = byteString.charCodeAt(i);
            }
            return new Blob([ab], { type: mimeString });
        }

        const image = ctx.canvas.toDataURL('image/png');
        if (options.download) {
            const link = document.createElement('a');
            const blob = dataURItoBlob(image);
            const url = URL.createObjectURL(blob);
            link.href = url;
            link.download = 'top3.png';
            link.click();
            URL.revokeObjectURL(url);
        }
        return image;
    }).catch(error => {
        console.log("One or more images failed to load:", error);
    });
};

const exportPng = (nickname, avatar, positiveList, negativeList) => {
    document.fonts.load('1px Alibaba-PuHuiTi').then(() => {
        drawPost(nickname, avatar, positiveList, negativeList);
    })

};

const renderPreview = () => {
    const demoPositive = [
        { id: 244931, names: ['示例正向 1'] },
        { id: 282031, names: ['示例正向 2'] },
        { id: 285757, names: ['示例正向 3'] }
    ];
    const demoNegative = [
        { id: 326859, names: ['示例反向 1'] },
        { id: 336268, names: ['示例反向 2'] },
        { id: 371829, names: ['示例反向 3'] }
    ];

    drawPost('AcuL', '/avatar.jpg', demoPositive, demoNegative, { download: false });
};

onMounted(() => {
    if (import.meta.env.DEV) {
        renderPreview();
    }
});

defineExpose({
    exportPng,
    renderPreview
})
</script>

<style scoped>
.poster-canvas {
    width: 540px;
    height: 1200px;
    border-radius: 12px;
    background: rgba(0, 0, 0, 0.1);
}
</style>
