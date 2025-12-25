import { Component, Input, OnChanges, SimpleChanges, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PlotlyModule } from 'angular-plotly.js';

@Component({
    selector: 'app-telemetry-chart',
    standalone: true,
    imports: [CommonModule, PlotlyModule],
    template: `
    <div class="chart-container">
      <plotly-plot
        [data]="graph.data"
        [layout]="graph.layout"
        [config]="graph.config"
        [useResizeHandler]="true"
        [style]="{position: 'relative', width: '100%', height: '100%'}">
      </plotly-plot>
    </div>
  `,
    styles: [`
    .chart-container {
      width: 100%;
      height: 400px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 8px;
      padding: 16px;
      box-sizing: border-box;
    }
  `]
})
export class TelemetryChartComponent implements OnChanges {
    @Input() xData: (number | string)[] = [];
    @Input() yData: number[] = [];
    @Input() title: string = 'Telemetry Data';
    @Input() yAxisTitle: string = 'Value';

    public graph = {
        data: [
            {
                x: [] as (number | string)[],
                y: [] as number[],
                type: 'scatter',
                mode: 'lines+markers',
                marker: { color: '#00e5ff' },
                line: { shape: 'spline', color: '#00e5ff' },
                name: 'Live Data'
            }
        ],
        layout: {
            title: {
                text: this.title,
                font: { color: '#ffffff', size: 18 }
            },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            xaxis: {
                gridcolor: 'rgba(255,255,255,0.1)',
                tickfont: { color: '#ffffff' },
                title: { text: 'Time', font: { color: '#ffffff' } }
            },
            yaxis: {
                gridcolor: 'rgba(255,255,255,0.1)',
                tickfont: { color: '#ffffff' },
                title: { text: this.yAxisTitle, font: { color: '#ffffff' } }
            },
            margin: { t: 50, r: 30, l: 60, b: 50 },
            autosize: true
        },
        config: {
            displayModeBar: false,
            responsive: true
        }
    };

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['xData'] || changes['yData']) {
            this.graph.data[0].x = [...this.xData];
            this.graph.data[0].y = [...this.yData];
        }
        if (changes['title']) {
            this.graph.layout.title.text = this.title;
        }
        if (changes['yAxisTitle']) {
            this.graph.layout.yaxis.title.text = this.yAxisTitle;
        }
    }
}
