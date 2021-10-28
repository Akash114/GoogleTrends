function interest(event) {
    event.preventDefault();
    $body = $("body");

    var data = document.getElementById('keyword').value;
    $.ajax({
        url: 'Trends/interest',
        type: 'POST',
        data: JSON.stringify({'keyword':data}),
        cache: false,
        processData: false,
        contentType: false,
        beforeSend:function() { $body.addClass("loading"); },
        success: function(data) {
            document.getElementById("result").style.display = 'block';
            document.getElementById("chartContainer").innerHTML = '<canvas id="chart" style="position: relative;"></canvas>';
            document.getElementById("heatmap").innerHTML = data.graph;
            document.getElementById("related").innerHTML = data.relateds.rendered_table;
            document.getElementById("queries").innerHTML = data.queries.queries_table;
            document.getElementById("trends").innerHTML = data.trends.rendered_table;
            let ctx = document.getElementById("chart").getContext("2d");

            let chart = new Chart(ctx, {
              type: 'line',
              data: {
                 labels: data.data.labels,
                 datasets: [
                    {
                      label: 'Searches',
                      backgroundColor: data.data.backgroundColor,
                        borderColor: "#417690",
                      data: data.data.data
                    }
                 ]
              },
              options: {
                 title: {
                    text: data.title,
                    display: true,
                     scales: {
                        yAxes: [{
                            ticks: {
                            beginAtZero: true
                            }
                        }]
                    }

                 },
                  maintainAspectRatio: false,
                  responsive: true,
              }
            });

            chart.canvas.parentNode.style.height = '512px';
            chart.canvas.parentNode.style.width = '620px';

            },
        complete:function(){$body.removeClass("loading");   }

    });
    return false;
    }