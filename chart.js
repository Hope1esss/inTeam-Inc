const data = {
    response: [
        [
            [432079965, 65],
            [483886774, 56],
            [88071442, 32],
            [264457326, 22],
            [380262599, 18]
        ],
        375
    ]
};

const lebels = data.response[0].map(item => item[0]);
const values = data.response[0].map(item => item[1]);

const ctx = document.getElementById('gifts').getContext('2d');
const myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: labels,
        datasets: [{
            label: '# of Votes',
            data: values,
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
