var frequency = '';

function dayswitch(day) {
    var freq = '';
    var color = '';
    var vibe = '';
    var theme = '';
    var hobby = '';

    switch(day) {
        case "Monday":
            freq = '396hz';
            color = 'Red';
            chakra = 'Root';
            vibe = 'Ground yourself and Release Fear';
            theme = 'Stability, security, grounding, survival';
            hobby = 'explore outdoors';
            break;
        case "Tuesday":
            freq = '417hz';
            color = 'Orange';
            chakra = 'Sacral';
            vibe = 'Stay Playful and expressive';
            theme = 'Creativity, emotions, sensuality, flow';
            hobby = 'write a poem';
            break;
        case "Wednesday":
            freq = '528hz';
            color = 'Yellow';
            chakra = 'Solar Plexus';
            vibe = 'Be energetic and focused';
            theme = 'Confidence, willpower, personal power';
            hobby = 'do yoga and strength-training';
            break;
        case "Thursday":
            freq = '639hz';
            color = 'Green';
            chakra = 'Heart';
            vibe = 'Stay open and nurturing';
            theme = 'Love, compassion, connection';
            hobby = 'journal and call someone you love';
            break;
        case "Friday":
            freq = '741hz';
            color = 'Blue';
            chakra = 'Throat';
            vibe = 'Be articulate and express yourself aunthentically';
            theme = 'Truth, self-expression, authenticity';
            hobby = 'write a reflective essay or a blog post';
            break;
        case "Saturday":
            freq = '852hz';
            color = 'Indigo';
            chakra = 'Third Eye';
            vibe = 'Work on inner seeing and connect to your vision';
            theme = 'Intuition, wisdom, clarity';
            hobby = 'read a philosophical text and do a visualization meditation';
            break;
}
    var dayhead = `<h1>Today is ${day}</h1></br>`;
    var minihead = `<h2>The frequency is ${freq} and the color is ${color}</h2>`
    var vibemsg = `<h3>Focus on the ${chakra} chakra: ${vibe}</h3></br>`;
    var hobbymsg = `<i>Make sure you ${hobby} today</i>`
    var thememsg = `<p><strong>Theme: </strong>${theme}</br></p>`
    var message = dayhead + minihead + vibemsg + thememsg + hobbymsg;
    return message;
}

document.write(dayswitch('Saturday'));