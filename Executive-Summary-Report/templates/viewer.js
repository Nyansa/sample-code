var data = REPORTDATA;
function create_layout() {
    try {
        var html = '';

        // Page Header
        if (data["title"] != "" || data["description"] != "") {
            var page_header = get_HTMLTemplate("page-header");
            page_header = page_header.replaceAll("{{title}}", data["title"]);
            page_header = page_header.replaceAll("{{description}}", data["description"]);
            page_header = page_header.replaceAll("{{company}}", data["company"]);
            page_header = page_header.replaceAll("{{date}}", data["date"]);
            html = page_header;
        }

        // Sections
        for (var section in data["sections"]) {

            // Section Body
            var section_body = get_HTMLTemplate("section-body");
            section_body = section_body.replaceAll("{{link}}", data["sections"][section]["link"]);

            // Section Header
            var section_header = get_HTMLTemplate("section-header");
            section_header = section_header.replaceAll("{{title}}", data["sections"][section]["title"]);
            section_header = section_header.replaceAll("{{description}}", data["sections"][section]["description"]);

            // Section Layout
            var section_layout = get_bootstrap_layout(data["sections"][section]["layout"]["rows"]);

            section_body = section_body.replaceAll("{{header}}", section_header);
            section_body = section_body.replaceAll("{{layout}}", section_layout);

            html = html + section_body;
        }

        var Content = document.getElementById("Content");
        Content.innerHTML = html;
    }
    catch (err) {
        console.log("create_layout: ERROR: " + err);
    }
}
function get_bootstrap_layout(layout) {
    try {
        var section_layout = '';
        for (var row in layout) {
            section_layout = section_layout + get_recursive_bootstrap_row(layout[row]["cols"]);
        }
        return section_layout;
    }
    catch (err) {
        console.log("get_bootstrap_layout: ERROR: " + err);
    }
}
function get_recursive_bootstrap_row(row) {
    try {
        var bootstrap_row = '<div class="row">';
        for (var col in row) {
            if (row[col].hasOwnProperty("rows") == true) {
                bootstrap_row = bootstrap_row + '<div class="col-' + row[col]["width"] + '">';
                bootstrap_row = bootstrap_row + get_recursive_bootstrap_row(row[col]["rows"]);
                bootstrap_row = bootstrap_row + '</div>';
            }
            else {
                if (row[col].hasOwnProperty("id") == true) {
                    bootstrap_row = bootstrap_row + '<div id="container-' + row[col]["id"] + '" class="col-' + row[col]["width"] + '"></div>';
                }
                else {
                    for (var col2 in row[col]["cols"]) {
                        bootstrap_row = bootstrap_row + '<div id="container-' + row[col]["cols"][col2]["id"] + '" class="col-' + row[col]["cols"][col2]["width"] + '"></div>';
                    }
                }
            }
        }
        bootstrap_row = bootstrap_row + '</div>';
        return bootstrap_row;
    }
    catch (err) {
        console.log("get_recursive_bootstrap_row: ERROR: " + err);
    }
}
// ---------------------------------------------------------------------------------------------------
// draw Charts
// ---------------------------------------------------------------------------------------------------
function draw_charts(context) {
    try {
        for (var section in data["sections"]) {
            for (var report in data["sections"][section]["reports"]) {
                if (data["sections"][section]["reports"][report]["id"].startsWith("info")) {
                    draw_info(context, section, report);
                }
                else {
                    draw_chart(context, section, report);
                }
            }
        }
    }
    catch (err) {
        console.log("draw_charts ERROR: " + err);
    }
}
function draw_chart(context, section, report) {
    try {
        var template = get_HTMLTemplate(data["sections"][section]["reports"][report]["id"]);
        if (template != null) {
            template = template.replaceAll("{{chart.title}}", data["sections"][section]["reports"][report]["config"]["title"]).replaceAll("{{chart.description}}", data["sections"][section]["reports"][report]["config"]["description"]).replaceAll("{{chart.id}}", data["sections"][section]["reports"][report]["id"]);
            var container = document.getElementById("container-" + data["sections"][section]["reports"][report]["id"]);
            container.innerHTML = template;

            var ChartLabels = get_ChartLabels(data["sections"][section]["reports"][report]["id"], section, report)
            var ChartData = get_ChartData(data["sections"][section]["reports"][report]["id"], ChartLabels.labels, ChartLabels.values, data["sections"][section]["reports"][report]["config"]["colors"]);
            var ChartOptions = get_ChartOptions(data["sections"][section]["reports"][report]["id"], ChartLabels.stepSize);

            if (ChartLabels != null && ChartData != null && ChartOptions != null) {
                context.charts.push(context.respChart($("#" + data["sections"][section]["reports"][report]["id"]), data["sections"][section]["reports"][report]["id"], ChartData, ChartOptions));

                var description = document.getElementById(data["sections"][section]["reports"][report]["id"] + '-description');
                if (description != null) {
                    if (description.innerHTML.includes('{{PERCENTAGE}}')) {
                        if (data["sections"][section]["reports"][report]["data"]["total"] == 0) {
                            description.innerHTML = '';
                        }
                        else {
                            description.innerHTML = description.innerHTML.replaceAll('{{PERCENTAGE}}', data["sections"][section]["reports"][report]["data"]["total"]);
                        }
                    }
                }

                if (data["sections"][section]["reports"][report]["id"].startsWith("donutchart")) {
                    draw_donut_legend(data["sections"][section]["reports"][report]["id"], section, report);
                }
            }
        }
    }
    catch (err) {
        console.log("draw_chart ERROR: " + err);
    }
}
function draw_donut_legend(id, section, report) {
    try {
        var template;
        if (id.startsWith("donutchart-vertical")) {
            template = get_HTMLTemplate("donut-legend-vertical");
        }
        else if (id.startsWith("donutchart-horizontal")) {
            template = get_HTMLTemplate("donut-legend-horizontal");
        }

        var html = '<table style="width: 100%">';
        var index = 0;
        for (var item in data["sections"][section]["reports"][report]["data"]["data"]) {
            html = html + template.replaceAll("{{LABEL}}", data["sections"][section]["reports"][report]["data"]["data"][item]["label"]).replaceAll("{{VALUE}}", data["sections"][section]["reports"][report]["data"]["data"][item]["value"] + " " + data["sections"][section]["reports"][report]["config"]["units"]).replaceAll("{{COLOR}}", data["sections"][section]["reports"][report]["config"]["colors"][index])
            index++;
        }
        html = html + '</table>';

        var container = document.getElementById(id + '-legend');
        container.innerHTML = html;
    }
    catch (err) {
        console.log("draw_donut_legend ID: " + id + " ERROR: " + err);
    }
}
function draw_info(context, section, report) {
    try {
        var template = get_HTMLTemplate(data["sections"][section]["reports"][report]["id"]);
        if (template != null) {

            template = template.replaceAll("{{chart.title}}", data["sections"][section]["reports"][report]["config"]["title"]);
            template = template.replaceAll("{{chart.color}}", data["sections"][section]["reports"][report]["config"]["color"]);
            template = template.replaceAll("{{chart.value}}", data["sections"][section]["reports"][report]["config"]["value"]);
            template = template.replaceAll("{{chart.count}}", data["sections"][section]["reports"][report]["config"]["count"]);

            var container = document.getElementById("container-" + data["sections"][section]["reports"][report]["id"]);
            container.innerHTML = template;
        }
    }
    catch (err) {
        console.log("draw_info ERROR: " + err);
    }
}
// ---------------------------------------------------------------------------------------------------
// Chart helper
// ---------------------------------------------------------------------------------------------------
function get_ChartLabels(id, section, report) {
    try {
        var result = { labels: [], values: [], stepSize: 0 };
        if (id == "barchart-vertical-application-performance") {
            for (var item in data["sections"][section]["reports"][report]["data"]) {
                result.labels.push([data["sections"][section]["reports"][report]["data"][item]["label"], data["sections"][section]["reports"][report]["data"][item]["value"] + " " + data["sections"][section]["reports"][report]["config"]["units"]]);
                result.values.push(data["sections"][section]["reports"][report]["data"][item]["value"]);
                if (data["sections"][section]["reports"][report]["data"][item]["value"] > result.stepSize) {
                    result.stepSize = data["sections"][section]["reports"][report]["data"][item]["value"];
                }
            }
            return result;
        }
        else if (id.startsWith("barchart-horizontal")) {
            for (var item in data["sections"][section]["reports"][report]["data"]) {
                if (data["sections"][section]["reports"][report]["config"]["units"] == "") {
                    result.labels.push(data["sections"][section]["reports"][report]["data"][item]["label"]);
                }
                else {
                    result.labels.push(data["sections"][section]["reports"][report]["data"][item]["label"] + " (" + data["sections"][section]["reports"][report]["data"][item]["value"] + " " + data["sections"][section]["reports"][report]["config"]["units"] + ")");
                }
                result.values.push(data["sections"][section]["reports"][report]["data"][item]["value"]);
                if (data["sections"][section]["reports"][report]["data"][item]["value"] > result.stepSize) {
                    result.stepSize = data["sections"][section]["reports"][report]["data"][item]["value"];
                }
            }
            return result;
        }
        else if (id.startsWith("donutchart")) {
            for (var item in data["sections"][section]["reports"][report]["data"]["data"]) {
                result.labels.push(data["sections"][section]["reports"][report]["data"]["data"][item]["label"] + " (" + data["sections"][section]["reports"][report]["data"]["data"][item]["value"] + " " + data["sections"][section]["reports"][report]["config"]["units"] + ")");
                result.values.push(data["sections"][section]["reports"][report]["data"]["data"][item]["value"]);
            }
            return result;
        }
    }
    catch (err) {
        console.log("get_ChartLabels: " + err);
    }
    return null;
}
function get_ChartData(id, labels, values, colors) {
    try {
        if (id.startsWith("barchart-horizontal")) {
            return {
                labels: labels,
                datasets: [
                    {
                        backgroundColor: colors,
                        data: values
                    }
                ]
            };
        }
        else if (id.startsWith("barchart-vertical")) {
            return {
                labels: labels,
                datasets: [
                    {
                        backgroundColor: colors,
                        data: values
                    }
                ]
            };
        }
        else if (id.startsWith("donutchart")) {
            return {
                labels: labels,
                datasets: [
                    {
                        data: values,
                        backgroundColor: colors,
                        borderWidth: "0",
                    }]
            };
        }
    }
    catch (err) {
        console.log("get_ChartData: " + err);
    }
    return null;
}
function get_ChartOptions(id, stepSize) {
    try {
        if (id.startsWith("barchart-horizontal")) {
            return {
                responsive: true,
                responsiveAnimationDuration: 0,
                maintainAspectRatio: false,
                legend: {
                    display: false
                },
                scales: {
                    xAxes: [{
                        gridLines: {
                            display: false,
                            color: "rgba(0,0,0,0.01)",
                            drawTicks: false
                        },
                        stacked: false,
                        ticks: {
                            display: false,
                            stepSize: stepSize
                        }
                    }],
                    yAxes: [{
                        barPercentage: 1,
                        categoryPercentage: 0.9,
                        stacked: false,
                        gridLines: {
                            color: "rgba(0,0,0,0.01)"
                        }
                    }]
                }
            };
        }
        else if (id.startsWith("barchart-vertical")) {
            return {
                responsive: true,
                responsiveAnimationDuration: 0,
                maintainAspectRatio: false,
                legend: {
                    display: false
                },
                scales: {
                    xAxes: [{
                        stacked: false,
                        gridLines: {
                            color: "rgba(0,0,0,0.01)"
                        }
                    }],
                    yAxes: [{
                        gridLines: {
                            display: false,
                            color: "rgba(0,0,0,0.01)",
                            drawTicks: false
                        },
                        stacked: false,
                        ticks: {
                            display: false,
                            stepSize: stepSize
                        }
                    }]
                }
            };
        }
        else if (id.startsWith("donutchart")) {
            return {
                responsive: true,
                responsiveAnimationDuration: 0,
                maintainAspectRatio: false,
                cutoutPercentage: 60,
                legend: {
                    display: false,
                    position: "bottom",
                    labels: {
                        boxWidth: 10
                    }
                }
            };
        }
    }
    catch (err) {
        console.log("get_ChartOptions: " + err);
    }
    return null;
}
// ---------------------------------------------------------------------------------------------------
// HTML Templates
// ---------------------------------------------------------------------------------------------------
function get_HTMLTemplate(id) {
    try {
        if (id.startsWith("barchart-horizontal-top10")) {
            return '<div class="card-body" style="padding-bottom: 20px">' +
                '    <div style="width: 100%">' +
                '        <div style="width: 50%; float: left; display: inline-block;">' +
                '            <h4 class="mb-0 mt-0">{{chart.title}}</h4>' +
                '        </div>' +
                '        <div style="width: 50%; float: right; display: inline-block; text-align: right">' +
                '            <p class="mb-0 mt-0">{{chart.description}}</p>' +
                '        </div>' +
                '    </div>' +
                '    <div class="mt-2 chartjs-chart" style="position: relative; height: 300px;">' +
                '        <canvas id="{{chart.id}}"></canvas>' +
                '    </div>' +
                '</div>';
        }
        else if (id.startsWith("barchart-horizontal")) {
            return '<div class="card-body" style="padding-bottom: 20px">' +
                '    <div style="width: 100%">' +
                '        <div style="width: 50%; float: left; display: inline-block;">' +
                '            <h4 class="mb-0 mt-0">{{chart.title}}</h4>' +
                '        </div>' +
                '        <div style="width: 50%; float: right; display: inline-block; text-align: right">' +
                '            <p class="mb-0 mt-0">{{chart.description}}</p>' +
                '        </div>' +
                '    </div>' +
                '    <div class="mt-2 chartjs-chart" style="position: relative; height: 150px;">' +
                '        <canvas id="{{chart.id}}"></canvas>' +
                '    </div>' +
                '</div>';
        }
        else if (id.startsWith("barchart-vertical")) {
            return '<div class="card-body" style="padding-left: 0px; padding-right: 0px; padding-bottom: 20px"" >' +
                '    <h4 class="mb-0" style="margin-left: 1.5rem">{{chart.title}}</h4>' +
                '    <p class="mb-0" style="margin-left: 1.5rem">{{chart.description}}</p>' +
                '    <div class="mt-3 chartjs-chart" style="position: relative; height: 300px;" >' +
                '        <canvas id="{{chart.id}}"></canvas>' +
                '    </div>' +
                '</div>';
        }
        else if (id.startsWith("donutchart-vertical")) {
            return '<div class="card-body" style="padding-bottom: 20px">' +
                '    <h5 class="mb-0">{{chart.title}}</h5>' +
                '    <p id="{{chart.id}}-description" class="mb-0" >{{chart.description}}</p>' +
                '    <div class="mb-2 mt-2 chartjs-chart" style="position: relative; height: 200px; max-width: 200px;">' +
                '        <canvas id="{{chart.id}}"></canvas>' +
                '    </div>' +
                '    <div id="{{chart.id}}-legend" class="chart-widget-list" style="margin-top: 10px">' +
                '    </div>' +
                '</div>';
        }
        else if (id.startsWith("donutchart-horizontal")) {
            return '<div class="card-body" style="padding-bottom: 20px">' +
                '    <div style="width: 100%; margin-bottom: 30px">' +
                '        <div style="width: 50%; float: left; display: inline-block;">' +
                '            <h5 class="mb-0">{{chart.title}}</h5>' +
                '        </div>' +
                '        <div style="width: 50%; float: right; display: inline-block; text-align: right">' +
                '            <p id="{{chart.id}}-description" class="font-13 mb-0">{{chart.description}}</p>' +
                '        </div>' +
                '    </div>' +
                '    <div style="width: 100%; margin: 0px; padding: 0px">' +
                '        <div style="height: 160px; float: left; display: inline-block;">' +
                '            <div class="chartjs-chart" style="position: relative; height: 160px; max-width: 160px">' +
                '                <canvas id="{{chart.id}}"></canvas>' +
                '            </div>' +
                '        </div>' +
                '        <div style="position: relative; height: 160px; float: left; display: inline-block">' +
                '            <div id="{{chart.id}}-legend" style="width: 200px; margin-left: 10px; position: absolute; top: 50%; transform: translateY(-50%);">' +
                '            </div>' +
                '        </div>' +
                '    </div>' +
                '</div>';
        }
        else if (id == "donut-legend-vertical") {
            return '<tr>' +
                '    <th style="width: 15px">' +
                '        <div style="height: 12px; width: 12px; display: inline-block; background-color:{{COLOR}}"></div>' +
                '    </th>' +
                '    <th style="max-width: 100px">' +
                '        <p style="margin: 0px; font-weight: normal; overflow: hidden; white-space: nowrap; text-overflow: ellipsis">{{LABEL}}</p>' +
                '    </th>' +
                '    <th style="text-align: right">' +
                '        <p style="margin: 0px; font-weight: normal">{{VALUE}}</p>' +
                '    </th>' +
                '</tr>';
        }
        else if (id == "donut-legend-horizontal") {
            return '<tr>' +
                '    <th style="width: 15px">' +
                '        <div style="height: 12px; width: 12px; display: inline-block; background-color:{{COLOR}}"></div>' +
                '    </th>' +
                '    <th>' +
                '        <p style="margin: 0px; font-weight: normal; overflow: hidden; white-space: nowrap; text-overflow: ellipsis">{{LABEL}}</p>' +
                '    </th>' +
                '    <th style="padding-left: 20px; text-align: right">' +
                '        <p style="margin: 0px; font-weight: normal">{{VALUE}}</p>' +
                '    </th>' +
                '</tr>';
        }
        else if (id.startsWith("info")) {
            return '<div class="card-body" style="padding-bottom: 20px">' +
                '    <div class="card" style="width: 100%; text-align: center; padding: 10px; background: {{chart.color}}; display: inline-block;">' +
                '        <h5 class="mb-2 text-white" >{{chart.title}}</h5>' +
                '        <h1 class="font-weight-bold text-white mb-2">{{chart.value}}</h1>' +
                '        <h5 class="mb-2 text-white" style="font-weight: normal">{{chart.count}}</h5>' +
                '    </div>' +
                '</div>';
        }
        else if (id == "page-header") {
            return '<div class="row" style="padding-bottom: 40px">' +
            '    <div class="col-xl-6">' +
            '        <h3>{{title}}</h3>' +
            '        <h5>{{description}}</h5>' +
            '    </div>' +
            '    <div class="col-xl-6" style="text-align: right">' +
            '        <h3>{{company}}</h3>' +
            '        <h5>{{date}}</h5>' +
            '    </div>' +
            '</div>';
        }
        else if (id == "section-header") {
            return '<div class="row" style="margin: 0px;">' +
                '    <div class="col-xl-12">' +
                '        <div style="width: 100%;">' +
                '            <div style="width: 50%; float: left; display: inline-block;">' +
                '                <h3>{{title}}</h3>' +
                '            </div>' +
                '            <div style="width: 50%; float: right; display: inline-block; text-align: right">' +
                '                <h5>{{description}}</h5>' +
                '            </div>' +
                '        </div>' +
                '    </div>' +
                '</div>';
        }
        else if (id == "section-body") {
            return '<div id="{{link}}" class="row" style="padding-bottom: 40px">' +
                '    <div class="col-xl-12">' +
                '        <div class="card" style="padding-top: 10px; padding-bottom: 20px">' +
                '            {{header}}' +
                '            {{layout}}' +
                '        </div>' +
                '    </div>' +
                '</div>';
        }
    }
    catch (err) {
        console.log("get_HTMLTemplate ID: " + id + " ERROR: " + err);
    }
    return null;
}
// ---------------------------------------------------------------------------------------------------
// JavaScript helper
// ---------------------------------------------------------------------------------------------------
String.prototype.replaceAll = function (search, replacement) {
    var target = this;
    return target.replace(new RegExp(search, 'g'), replacement);
};
// ---------------------------------------------------------------------------------------------------
// Charts.js
// ---------------------------------------------------------------------------------------------------
window.onload = function (e) {
    ChartJs = new ChartJs, ChartJs.Constructor = ChartJs;
    ChartJs.init();
}
var ChartJs = function () { this.$body = $("body"), this.charts = [] };
ChartJs.prototype.respChart = function (selector, type, data, options) {

    var draw = Chart.controllers.line.prototype.draw;
    Chart.controllers.line.prototype.draw = function () {
        draw.apply(this, arguments);
        var ctx = this.chart.chart.ctx;
        var _stroke = ctx.stroke;
        ctx.stroke = function () {
            ctx.save();
            ctx.shadowColor = 'rgba(0,0,0,0.01)';
            ctx.shadowBlur = 20;
            ctx.shadowOffsetX = 0;
            ctx.shadowOffsetY = 5;
            _stroke.apply(this, arguments);
            ctx.restore();
        }
    };

    var draw2 = Chart.controllers.doughnut.prototype.draw;
    Chart.controllers.doughnut = Chart.controllers.doughnut.extend({
        draw: function () {
            draw2.apply(this, arguments);
            var ctx = this.chart.chart.ctx;
            var _fill = ctx.fill;
            ctx.fill = function () {
                ctx.save();
                ctx.shadowColor = 'rgba(0,0,0,0.03)';
                ctx.shadowBlur = 4;
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 3;
                _fill.apply(this, arguments)
                ctx.restore();
            }
        }
    });

    var draw3 = Chart.controllers.bar.prototype.draw;
    Chart.controllers.bar = Chart.controllers.bar.extend({
        draw: function () {
            draw3.apply(this, arguments);
            var ctx = this.chart.chart.ctx;
            var _fill = ctx.fill;
            ctx.fill = function () {
                ctx.save();
                ctx.shadowColor = 'rgba(0,0,0,0.01)';
                ctx.shadowBlur = 20;
                ctx.shadowOffsetX = 4;
                ctx.shadowOffsetY = 5;
                _fill.apply(this, arguments)
                ctx.restore();
            }
        }
    });

    // get selector by context
    var ctx = selector.get(0).getContext("2d");

    // pointing parent container to make chart js inherit its width
    var container = $(selector).parent();

    // this function produce the responsive Chart JS
    function generateChart() {
        var ww = selector.attr('width', $(container).width());
        var chart;
        if (type.startsWith("linechart")) {
            chart = new Chart(ctx, { type: 'line', data: data, options: options });
        }
        else if (type.startsWith("donutchart")) {
            chart = new Chart(ctx, { type: 'doughnut', data: data, options: options });
        }
        else if (type.startsWith("piechart")) {
            chart = new Chart(ctx, { type: 'pie', data: data, options: options });
        }
        else if (type.startsWith("barchart-vertical")) {
            chart = new Chart(ctx, { type: 'bar', data: data, options: options });
        }
        else if (type.startsWith("barchart-horizontal")) {
            chart = new Chart(ctx, { type: 'horizontalBar', data: data, options: options });
        }
        else if (type.startsWith("radarchart")) {
            chart = new Chart(ctx, { type: 'radar', data: data, options: options });
        }
        else if (type.startsWith("polarareachart")) {
            chart = new Chart(ctx, { type: 'polarArea', data: data, options: options });
        }
        return chart;
    };

    return generateChart();
}
ChartJs.prototype.initCharts = function () {
    var charts = [];

    create_layout();
    draw_charts(this);

    return charts;
}
ChartJs.prototype.init = function () {
    var $this = this;
    // font
    Chart.defaults.global.defaultFontFamily = '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Oxygen-Sans,Ubuntu,Cantarell,"Helvetica Neue",sans-serif';
    // init charts
    $this.charts = this.initCharts();
    // enable resizing matter
    $(window).on('resize', function (e) {
        $.each($this.charts, function (index, chart) {
            try {
                chart.destroy();
            }
            catch (err) {
            }
        });
        $this.charts = $this.initCharts();
    });
}
