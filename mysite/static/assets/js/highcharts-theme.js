// Apply theme based on current data-bs-theme
function applyHighchartsTheme() {
    const theme = document.documentElement.getAttribute('data-bs-theme') || 'dark';
    
    if (theme === 'dark') {
        Highcharts.setOptions({
            chart: {
                backgroundColor: '#212529',
                style: {
                    fontFamily: '\'Unica One\', sans-serif'
                },
                plotBorderColor: '#606063'
            },
            title: {
                style: {
                    color: '#dee2e6',
                    textTransform: 'uppercase',
                    fontSize: '20px'
                }
            },
            xAxis: {
                gridLineColor: '#707073',
                labels: {
                    style: {
                        color: '#dee2e6'
                    }
                },
                lineColor: '#707073',
                minorGridLineColor: '#505053',
                tickColor: '#707073',
                title: {
                    style: {
                        color: '#A0A0A3'
                    }
                }
            },
            yAxis: {
                gridLineColor: '#707073',
                labels: {
                    style: {
                        color: '#dee2e6'
                    }
                },
                lineColor: '#707073',
                minorGridLineColor: '#505053',
                tickColor: '#707073',
                tickWidth: 1,
                title: {
                    style: {
                        color: '#A0A0A3'
                    }
                }
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.85)',
                style: {
                    color: '#F0F0F0'
                }
            },
            plotOptions: {
                series: {
                    dataLabels: {
                        color: '#B0B0B3'
                    },
                    marker: {
                        lineColor: '#333'
                    }
                },
                boxplot: {
                    fillColor: '#505053'
                },
                candlestick: {
                    lineColor: 'white'
                },
                errorbar: {
                    color: 'white'
                }
            },
            legend: {
                itemStyle: {
                    color: '#E0E0E3'
                },
                itemHoverStyle: {
                    color: '#FFF'
                },
                itemHiddenStyle: {
                    color: '#606063'
                }
            },
            credits: {
                style: {
                    color: '#666'
                }
            },
            labels: {
                style: {
                    color: '#707073'
                }
            }
        });
    } else {
        Highcharts.setOptions({
            chart: {
                backgroundColor: '#ffffff',
                style: {
                    fontFamily: '\'Unica One\', sans-serif'
                },
                plotBorderColor: '#ccc'
            },
            title: {
                style: {
                    color: '#212529',
                    textTransform: 'uppercase',
                    fontSize: '20px'
                }
            },
            xAxis: {
                gridLineColor: '#e0e0e0',
                labels: {
                    style: {
                        color: '#212529'
                    }
                },
                lineColor: '#ccc',
                minorGridLineColor: '#f0f0f0',
                tickColor: '#ccc',
                title: {
                    style: {
                        color: '#555555'
                    }
                }
            },
            yAxis: {
                gridLineColor: '#e0e0e0',
                labels: {
                    style: {
                        color: '#212529'
                    }
                },
                lineColor: '#ccc',
                minorGridLineColor: '#f0f0f0',
                tickColor: '#ccc',
                tickWidth: 1,
                title: {
                    style: {
                        color: '#555555'
                    }
                }
            },
            tooltip: {
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                borderColor: '#ccc',
                style: {
                    color: '#212529'
                }
            },
            plotOptions: {
                series: {
                    dataLabels: {
                        color: '#333'
                    },
                    marker: {
                        lineColor: '#ccc'
                    }
                },
                boxplot: {
                    fillColor: '#e0e0e0'
                },
                candlestick: {
                    lineColor: '#000'
                },
                errorbar: {
                    color: '#000'
                }
            },
            legend: {
                itemStyle: {
                    color: '#212529'
                },
                itemHoverStyle: {
                    color: '#000'
                },
                itemHiddenStyle: {
                    color: '#ccc'
                }
            },
            credits: {
                style: {
                    color: '#999'
                }
            },
            labels: {
                style: {
                    color: '#ccc'
                }
            }
        });
    }
}

// Apply initial theme
applyHighchartsTheme();

// Listen for theme changes
document.addEventListener('themeChanged', function() {
    applyHighchartsTheme();
});