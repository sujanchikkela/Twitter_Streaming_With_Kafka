var bar_chart = document.getElementById('hashtag_bar_chart').getContext('2d');
var hashtag_bar_chart = new Chart(bar_chart, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            label: 'hastag',
            data: [],
            backgroundColor:'rgba(54, 162, 235, 0.2)',
            borderColor:'rgb(54, 162, 235)',
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            yAxes: [{
                stacked: true,
                ticks: {
                    beginAtZero: true,
                    callback: function(value) {if (value % 1 === 0) {return value;}}
                }
            }]
        }
    }
});

var hashtag_trending_data= {
    labels: [],
    counts: []
}

setInterval(function(){
    $.getJSON('/refresh_trending', {
    }, function(data) {
        hashtag_trending_data.labels = data.Label;
        hashtag_trending_data.counts = data.Count;
    });
    hashtag_bar_chart.data.labels = hashtag_trending_data.labels;
    hashtag_bar_chart.data.datasets[0].data = hashtag_trending_data.counts;
    hashtag_bar_chart.update();
},2000);