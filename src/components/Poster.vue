<template>
    <canvas ref="posterCanvas" width="540" height="1200"></canvas>
</template>

<script setup>
import { ref } from 'vue';

const posterCanvas = ref(null);

const drawPost = (nickname, avatar, positiveList, negativeList) => {
    const canvas = posterCanvas.value;
    const ctx = canvas.getContext("2d");

    function drawLine(x1, y1, x2, y2) {
        const canvas = posterCanvas.value;
        const ctx = canvas.getContext("2d");

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

    function loadImage(src, isLocal=false) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.crossOrigin = 'anonymous';
            img.src =  isLocal ? src : `https://search.bgmss.fun/proxy?url=${src}`;
            img.onload = () => resolve(img);
            img.onerror = reject;
        });
    }

    function drawRadiuImg(x, y, width, height, radius, img) {
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
        loadImage(avatar), 
        loadImage('/bgm不知道多少.png', true),
        loadImage('/bgm38.png', true),
        loadImage(positiveList[1].image),
        loadImage(positiveList[0].image),
        loadImage(positiveList[2].image),
        loadImage(negativeList[1].image),
        loadImage(negativeList[2].image),
        loadImage(negativeList[0].image),
    ]).then(([avatarImg, bgmBzdImg, bgm38Img, p1, p2, p3, n1, n2, n3]) => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        gradient.addColorStop(0, "#0F0D10");
        gradient.addColorStop(0.5, "#253141");
        gradient.addColorStop(1, "#7d4e71");

        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#ffffff'; 

        let fontSize = 65; 
        ctx.font = 'lighter 65px AlimamaFangYuanTiVF'; 
        const userName = nickname;
        let textWidth = ctx.measureText(userName).width;
        while (textWidth > 340 && fontSize > 30) {
            fontSize -= 1; 
            ctx.font = `lighter ${fontSize}px AlimamaFangYuanTiVF`;
            textWidth = ctx.measureText(userName).width;
        }
        ctx.fillText(userName, 30, 85); 

        ctx.font = 'lighter 27px AlimamaFangYuanTiVF'; 
        const titleDescription = "的个人年度新番 Top3";
        ctx.fillText(titleDescription, 30, 135); 

        ctx.font = 'lighter 20px AlimamaFangYuanTiVF'; 
        drawWrappedText(ctx, 'top3.bgmss.fun', canvas.width / 2, 1150, 1200, 100);
        drawWrappedText(ctx, '选出你的年度新番 Top3', canvas.width / 2, 1180, 1200, 100);

        drawLine(27, 168, 510, 168);
        drawLine(27, 1115, 510, 1115);

        ctx.font = 'lighter 40px AlimamaFangYuanTiVF';
        const positiveTop3 = "正向 Top3";
        ctx.fillText(positiveTop3, 85, 225); 

        const negativeTop3 = "反向 Top3";
        ctx.fillText(negativeTop3, 268, 1078); 


        const positiveTop1Gradient = ctx.createLinearGradient(194, 264, 194, 264+388);
        positiveTop1Gradient.addColorStop(0, 'rgba(255, 216, 112, 1)');
        positiveTop1Gradient.addColorStop(0.5, 'rgba(96, 84, 69, 0.1)');
        positiveTop1Gradient.addColorStop(1, 'rgba(85, 63, 77, 0.0)');
        drawRoundRect(194, 264, 148, 388, 10, positiveTop1Gradient);

        const positiveTop2Gradient = ctx.createLinearGradient(27, 307, 27, 307+388);
        positiveTop2Gradient.addColorStop(0, 'rgba(175, 175, 175, 1)');
        positiveTop2Gradient.addColorStop(0.5, 'rgba(90, 90, 90, 0.1)');
        positiveTop2Gradient.addColorStop(1, 'rgba(85, 63, 77, 0.0)');
        drawRoundRect(27, 307, 148, 388, 10, positiveTop2Gradient);

        const positiveTop3Gradient = ctx.createLinearGradient(363, 307, 363, 307+388);
        positiveTop3Gradient.addColorStop(0, 'rgba(126, 92, 53, 1)');
        positiveTop3Gradient.addColorStop(0.5, 'rgba(81, 65, 59, 0.1)');
        positiveTop3Gradient.addColorStop(1, 'rgba(85, 63, 77, 0.0)');
        drawRoundRect(363, 307, 148, 388, 10, positiveTop3Gradient);

        const negativeTop1Gradient = ctx.createLinearGradient(194, 623, 194, 623+388);
        negativeTop1Gradient.addColorStop(1, 'rgba(255, 216, 112, 1)');
        negativeTop1Gradient.addColorStop(0.5, 'rgba(113, 87, 98, 0.1)');
        negativeTop1Gradient.addColorStop(0, 'rgba(85, 63, 77, 0.0)');
        drawRoundRect(194, 623, 148, 388, 10, negativeTop1Gradient);

        const negativeTop2Gradient = ctx.createLinearGradient(363, 582, 363, 582+388);
        negativeTop2Gradient.addColorStop(1, 'rgba(175, 175, 175, 1)');
        negativeTop2Gradient.addColorStop(0.5, 'rgba(90, 90, 90, 0.1)');
        negativeTop2Gradient.addColorStop(0, 'rgba(85, 63, 77, 0.0)');
        drawRoundRect(363, 582, 148, 388, 10, negativeTop2Gradient);

        const negativeTop3Gradient = ctx.createLinearGradient(27, 582, 27, 582+388);
        negativeTop3Gradient.addColorStop(1, 'rgba(126, 92, 53, 1)');
        negativeTop3Gradient.addColorStop(0.5, 'rgba(81, 65, 59, 0.1)');
        negativeTop3Gradient.addColorStop(0, 'rgba(85, 63, 77, 0.0)');
        drawRoundRect(27, 582, 148, 388, 10, negativeTop3Gradient);


        const positiveTop1TextGradient = ctx.createLinearGradient(255, 280, 255, 313);
        positiveTop1TextGradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        positiveTop1TextGradient.addColorStop(1, 'rgba(227, 196, 114, 1)');
        ctx.font = 'lighter 45px AlimamaFangYuanTiVF';
        ctx.fillStyle = positiveTop1TextGradient;
        ctx.fillText('1', 262, 310);

        const positiveTop2TextGradient = ctx.createLinearGradient(90, 321, 90, 356);
        positiveTop2TextGradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        positiveTop2TextGradient.addColorStop(1, 'rgba(200, 198, 200, 1)');
        ctx.font = 'lighter 45px AlimamaFangYuanTiVF';
        ctx.fillStyle = positiveTop2TextGradient;
        ctx.fillText('2', 90, 356);

        const positiveTop3TextGradient = ctx.createLinearGradient(425, 321, 425, 356);
        positiveTop3TextGradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        positiveTop3TextGradient.addColorStop(1, 'rgba(204, 154, 105, 1)');
        ctx.font = 'lighter 45px AlimamaFangYuanTiVF';
        ctx.fillStyle = positiveTop3TextGradient;
        ctx.fillText('3', 425, 356);

        const negativeTop1TextGradient = ctx.createLinearGradient(255, 988, 255, 954);
        negativeTop1TextGradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        negativeTop1TextGradient.addColorStop(1, 'rgba(227, 196, 114, 1)');
        ctx.font = 'lighter 45px AlimamaFangYuanTiVF';
        ctx.fillStyle = negativeTop1TextGradient;
        ctx.fillText('1', 262, 988);

        const negativeTop2TextGradient = ctx.createLinearGradient(425, 947, 425, 912);
        negativeTop2TextGradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        negativeTop2TextGradient.addColorStop(1, 'rgba(200, 198, 200, 1)');
        ctx.font = 'lighter 45px AlimamaFangYuanTiVF';
        ctx.fillStyle = negativeTop2TextGradient;
        ctx.fillText('2', 425, 947);

        const negativeTop3TextGradient = ctx.createLinearGradient(90, 947, 90, 912);
        negativeTop3TextGradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        negativeTop3TextGradient.addColorStop(1, 'rgba(204, 154, 105, 1)');
        ctx.font = 'lighter 45px AlimamaFangYuanTiVF';
        ctx.fillStyle = negativeTop3TextGradient;
        ctx.fillText('3', 90, 947);


        ctx.fillStyle = '#ffffff';
        ctx.font = 'lighter 18px AlimamaFangYuanTiVF';
        
        const positiveTop1Name = positiveList[1].name;
        drawWrappedText(ctx, positiveTop1Name, 268, 532, 150, 25); 
        const positiveTop2Name = positiveList[0].name;
        drawWrappedText(ctx, positiveTop2Name, 102, 576, 150, 25); 
        const positiveTop3Name = positiveList[2].name;
        drawWrappedText(ctx, positiveTop3Name, 440, 576, 150, 25); 

        const negativeTop1Name = negativeList[1].name;
        drawWrappedTextBottomLeft(ctx, negativeTop1Name, 268, 748, 150, 25); 
        const negativeTop2Name = negativeList[2].name;
        drawWrappedTextBottomLeft(ctx, negativeTop2Name, 102, 705, 150, 25); 
        const negativeTop3Name = negativeList[0].name;
        drawWrappedTextBottomLeft(ctx, negativeTop3Name, 440, 705, 150, 25); 


        drawRadiuImg(390, 25, 120, 120, 15, avatarImg);
        ctx.drawImage(bgmBzdImg, 32, 190, 40, 40);
        ctx.drawImage(bgm38Img, 465, 1040, 40, 40);
        drawRadiuImg(206, 326, 124, 175, 8, p1);
        drawRadiuImg(39, 370, 124, 175, 8, p2);
        drawRadiuImg(375, 370, 124, 175, 8, p3);
        drawRadiuImg(206, 763, 124, 175, 8, n1);
        drawRadiuImg(39, 722, 124, 175, 8, n2);
        drawRadiuImg(375, 722, 124, 175, 8, n3);

        
        const image = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.href = image;
        link.download = 'top3.png';
        link.click();
    }).catch(error => {
        console.error("One or more images failed to load:", error);
    });
};

const exportPng = (nickname, avatar, positiveList, negativeList) => {
    document.fonts.load('1px AlimamaFangYuanTiVF').then(() => {
        drawPost(nickname, avatar, positiveList, negativeList);
    })
    
};

defineExpose({
    exportPng
})
</script>