<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()>
Partial Class Scope_Channel_Display
	Inherits System.Windows.Forms.UserControl

	'UserControl overrides dispose to clean up the component list.
	<System.Diagnostics.DebuggerNonUserCode()>
	Protected Overrides Sub Dispose(ByVal disposing As Boolean)
		Try
			If disposing AndAlso components IsNot Nothing Then
				components.Dispose()
			End If
		Finally
			MyBase.Dispose(disposing)
		End Try
	End Sub

	'Required by the Windows Form Designer
	Private components As System.ComponentModel.IContainer

	'NOTE: The following procedure is required by the Windows Form Designer
	'It can be modified using the Windows Form Designer.  
	'Do not modify it using the code editor.
	<System.Diagnostics.DebuggerStepThrough()>
	Private Sub InitializeComponent()
		Me.components = New System.ComponentModel.Container()
		Dim ChartArea1 As System.Windows.Forms.DataVisualization.Charting.ChartArea = New System.Windows.Forms.DataVisualization.Charting.ChartArea()
		Dim Series1 As System.Windows.Forms.DataVisualization.Charting.Series = New System.Windows.Forms.DataVisualization.Charting.Series()
		Dim DataPoint1 As System.Windows.Forms.DataVisualization.Charting.DataPoint = New System.Windows.Forms.DataVisualization.Charting.DataPoint(0R, 0R)
		Me.TextBox_SCOPE_Title = New System.Windows.Forms.TextBox()
		Me.ContextMenuStrip1 = New System.Windows.Forms.ContextMenuStrip(Me.components)
		Me.ToolStripSeparator1 = New System.Windows.Forms.ToolStripSeparator()
		Me.Button_RouteMe = New System.Windows.Forms.Button()
		Me.Button_FFT = New System.Windows.Forms.Button()
		Me.Button_Autoscale = New System.Windows.Forms.Button()
		Me.TableLayoutPanel1 = New System.Windows.Forms.TableLayoutPanel()
		Me.TableLayoutPanel4 = New System.Windows.Forms.TableLayoutPanel()
		Me.TrackBar_Horizontal = New System.Windows.Forms.TrackBar()
		Me.TextBox_TimeBase = New System.Windows.Forms.TextBox()
		Me.display_VPP = New APK_Bench_Software.Horizontal_Meter_With_Text()
		Me.TableLayoutPanel3 = New System.Windows.Forms.TableLayoutPanel()
		Me.display_Vrms = New APK_Bench_Software.Horizontal_Meter_With_Text()
		Me.display_dBm = New APK_Bench_Software.Horizontal_Meter_With_Text()
		Me.CheckBox_freq = New System.Windows.Forms.CheckBox()
		Me.CheckBox_VPP = New System.Windows.Forms.CheckBox()
		Me.CheckBox_Vrms = New System.Windows.Forms.CheckBox()
		Me.display_freq = New APK_Bench_Software.Horizontal_Meter_With_Text()
		Me.TableLayoutPanel6 = New System.Windows.Forms.TableLayoutPanel()
		Me.CheckBox_graph = New System.Windows.Forms.CheckBox()
		Me.TrackBar_GraphDelay = New System.Windows.Forms.TrackBar()
		Me.TrackBar_Number_Of_Averages = New System.Windows.Forms.TrackBar()
		Me.CheckBox_Averaging = New System.Windows.Forms.CheckBox()
		Me.TableLayoutPanel2 = New System.Windows.Forms.TableLayoutPanel()
		Me.TextBox_vertical = New System.Windows.Forms.TextBox()
		Me.TrackBar_Vertical = New System.Windows.Forms.TrackBar()
		Me.TableLayoutPanel_MAIN = New System.Windows.Forms.TableLayoutPanel()
		Me.TimeChart = New System.Windows.Forms.DataVisualization.Charting.Chart()
		Me.ContextMenuStrip1.SuspendLayout()
		Me.TableLayoutPanel1.SuspendLayout()
		Me.TableLayoutPanel4.SuspendLayout()
		CType(Me.TrackBar_Horizontal, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.TableLayoutPanel3.SuspendLayout()
		Me.TableLayoutPanel6.SuspendLayout()
		CType(Me.TrackBar_GraphDelay, System.ComponentModel.ISupportInitialize).BeginInit()
		CType(Me.TrackBar_Number_Of_Averages, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.TableLayoutPanel2.SuspendLayout()
		CType(Me.TrackBar_Vertical, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.TableLayoutPanel_MAIN.SuspendLayout()
		CType(Me.TimeChart, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.SuspendLayout()
		'
		'TextBox_SCOPE_Title
		'
		Me.TextBox_SCOPE_Title.Dock = System.Windows.Forms.DockStyle.Top
		Me.TextBox_SCOPE_Title.Font = New System.Drawing.Font("Microsoft Sans Serif", 18.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.TextBox_SCOPE_Title.Location = New System.Drawing.Point(0, 0)
		Me.TextBox_SCOPE_Title.Margin = New System.Windows.Forms.Padding(0)
		Me.TextBox_SCOPE_Title.MaxLength = 6
		Me.TextBox_SCOPE_Title.Name = "TextBox_SCOPE_Title"
		Me.TextBox_SCOPE_Title.Size = New System.Drawing.Size(1473, 35)
		Me.TextBox_SCOPE_Title.TabIndex = 217
		Me.TextBox_SCOPE_Title.Tag = "Chan 1"
		Me.TextBox_SCOPE_Title.Text = "Chan 1"
		'
		'ContextMenuStrip1
		'
		Me.ContextMenuStrip1.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.ToolStripSeparator1})
		Me.ContextMenuStrip1.Name = "ContextMenuStrip1"
		Me.ContextMenuStrip1.Size = New System.Drawing.Size(61, 10)
		'
		'ToolStripSeparator1
		'
		Me.ToolStripSeparator1.Name = "ToolStripSeparator1"
		Me.ToolStripSeparator1.Size = New System.Drawing.Size(57, 6)
		'
		'Button_RouteMe
		'
		Me.Button_RouteMe.Dock = System.Windows.Forms.DockStyle.Fill
		Me.Button_RouteMe.Location = New System.Drawing.Point(0, 0)
		Me.Button_RouteMe.Margin = New System.Windows.Forms.Padding(0)
		Me.Button_RouteMe.Name = "Button_RouteMe"
		Me.Button_RouteMe.Size = New System.Drawing.Size(184, 48)
		Me.Button_RouteMe.TabIndex = 227
		Me.Button_RouteMe.Text = "Route To Me"
		Me.Button_RouteMe.UseVisualStyleBackColor = True
		'
		'Button_FFT
		'
		Me.Button_FFT.Dock = System.Windows.Forms.DockStyle.Fill
		Me.Button_FFT.Location = New System.Drawing.Point(184, 48)
		Me.Button_FFT.Margin = New System.Windows.Forms.Padding(0)
		Me.Button_FFT.Name = "Button_FFT"
		Me.Button_FFT.Size = New System.Drawing.Size(184, 49)
		Me.Button_FFT.TabIndex = 228
		Me.Button_FFT.Text = "FFT"
		Me.Button_FFT.UseVisualStyleBackColor = True
		'
		'Button_Autoscale
		'
		Me.Button_Autoscale.Dock = System.Windows.Forms.DockStyle.Fill
		Me.Button_Autoscale.Location = New System.Drawing.Point(0, 48)
		Me.Button_Autoscale.Margin = New System.Windows.Forms.Padding(0)
		Me.Button_Autoscale.Name = "Button_Autoscale"
		Me.Button_Autoscale.Size = New System.Drawing.Size(184, 49)
		Me.Button_Autoscale.TabIndex = 232
		Me.Button_Autoscale.Text = "Autoscale"
		Me.Button_Autoscale.UseVisualStyleBackColor = True
		'
		'TableLayoutPanel1
		'
		Me.TableLayoutPanel1.ColumnCount = 4
		Me.TableLayoutPanel1.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 25.0!))
		Me.TableLayoutPanel1.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 25.0!))
		Me.TableLayoutPanel1.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 25.0!))
		Me.TableLayoutPanel1.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 25.0!))
		Me.TableLayoutPanel1.Controls.Add(Me.TableLayoutPanel4, 0, 2)
		Me.TableLayoutPanel1.Controls.Add(Me.display_VPP, 1, 0)
		Me.TableLayoutPanel1.Controls.Add(Me.TableLayoutPanel3, 1, 2)
		Me.TableLayoutPanel1.Controls.Add(Me.display_Vrms, 2, 0)
		Me.TableLayoutPanel1.Controls.Add(Me.display_dBm, 3, 0)
		Me.TableLayoutPanel1.Controls.Add(Me.CheckBox_freq, 0, 1)
		Me.TableLayoutPanel1.Controls.Add(Me.CheckBox_VPP, 1, 1)
		Me.TableLayoutPanel1.Controls.Add(Me.CheckBox_Vrms, 2, 1)
		Me.TableLayoutPanel1.Controls.Add(Me.display_freq, 0, 0)
		Me.TableLayoutPanel1.Controls.Add(Me.TableLayoutPanel6, 3, 2)
		Me.TableLayoutPanel1.Controls.Add(Me.TableLayoutPanel2, 2, 2)
		Me.TableLayoutPanel1.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TableLayoutPanel1.Location = New System.Drawing.Point(0, 712)
		Me.TableLayoutPanel1.Margin = New System.Windows.Forms.Padding(0)
		Me.TableLayoutPanel1.Name = "TableLayoutPanel1"
		Me.TableLayoutPanel1.RowCount = 3
		Me.TableLayoutPanel1.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 47.81022!))
		Me.TableLayoutPanel1.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 12.0438!))
		Me.TableLayoutPanel1.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 40.0!))
		Me.TableLayoutPanel1.Size = New System.Drawing.Size(1473, 238)
		Me.TableLayoutPanel1.TabIndex = 232
		'
		'TableLayoutPanel4
		'
		Me.TableLayoutPanel4.ColumnCount = 1
		Me.TableLayoutPanel4.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 100.0!))
		Me.TableLayoutPanel4.Controls.Add(Me.TrackBar_Horizontal, 0, 1)
		Me.TableLayoutPanel4.Controls.Add(Me.TextBox_TimeBase, 0, 0)
		Me.TableLayoutPanel4.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TableLayoutPanel4.Location = New System.Drawing.Point(0, 141)
		Me.TableLayoutPanel4.Margin = New System.Windows.Forms.Padding(0)
		Me.TableLayoutPanel4.Name = "TableLayoutPanel4"
		Me.TableLayoutPanel4.RowCount = 2
		Me.TableLayoutPanel4.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel4.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel4.Size = New System.Drawing.Size(368, 97)
		Me.TableLayoutPanel4.TabIndex = 235
		'
		'TrackBar_Horizontal
		'
		Me.TrackBar_Horizontal.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TrackBar_Horizontal.LargeChange = 1
		Me.TrackBar_Horizontal.Location = New System.Drawing.Point(3, 51)
		Me.TrackBar_Horizontal.Maximum = 30
		Me.TrackBar_Horizontal.Name = "TrackBar_Horizontal"
		Me.TrackBar_Horizontal.Size = New System.Drawing.Size(362, 43)
		Me.TrackBar_Horizontal.TabIndex = 233
		'
		'TextBox_TimeBase
		'
		Me.TextBox_TimeBase.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TextBox_TimeBase.Location = New System.Drawing.Point(0, 0)
		Me.TextBox_TimeBase.Margin = New System.Windows.Forms.Padding(0)
		Me.TextBox_TimeBase.Name = "TextBox_TimeBase"
		Me.TextBox_TimeBase.Size = New System.Drawing.Size(368, 20)
		Me.TextBox_TimeBase.TabIndex = 232
		'
		'display_VPP
		'
		Me.display_VPP.AllowDrop = True
		Me.display_VPP.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink
		Me.display_VPP.BackColor = System.Drawing.Color.Black
		Me.display_VPP.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
		Me.display_VPP.Dock = System.Windows.Forms.DockStyle.Fill
		Me.display_VPP.Location = New System.Drawing.Point(368, 0)
		Me.display_VPP.Margin = New System.Windows.Forms.Padding(0)
		Me.display_VPP.ModuleNumber = 0R
		Me.display_VPP.Name = "display_VPP"
		Me.display_VPP.Size = New System.Drawing.Size(368, 113)
		Me.display_VPP.TabIndex = 212
		Me.display_VPP.Title_To_Display = "VPP"
		Me.display_VPP.Value_To_Display = 0R
		Me.display_VPP.Visible = False
		'
		'TableLayoutPanel3
		'
		Me.TableLayoutPanel3.ColumnCount = 2
		Me.TableLayoutPanel3.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel3.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel3.Controls.Add(Me.Button_Autoscale, 0, 1)
		Me.TableLayoutPanel3.Controls.Add(Me.Button_FFT, 1, 1)
		Me.TableLayoutPanel3.Controls.Add(Me.Button_RouteMe, 0, 0)
		Me.TableLayoutPanel3.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TableLayoutPanel3.Location = New System.Drawing.Point(368, 141)
		Me.TableLayoutPanel3.Margin = New System.Windows.Forms.Padding(0)
		Me.TableLayoutPanel3.Name = "TableLayoutPanel3"
		Me.TableLayoutPanel3.RowCount = 2
		Me.TableLayoutPanel3.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel3.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel3.Size = New System.Drawing.Size(368, 97)
		Me.TableLayoutPanel3.TabIndex = 233
		'
		'display_Vrms
		'
		Me.display_Vrms.AllowDrop = True
		Me.display_Vrms.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink
		Me.display_Vrms.BackColor = System.Drawing.Color.Black
		Me.display_Vrms.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
		Me.display_Vrms.Dock = System.Windows.Forms.DockStyle.Fill
		Me.display_Vrms.Location = New System.Drawing.Point(736, 0)
		Me.display_Vrms.Margin = New System.Windows.Forms.Padding(0)
		Me.display_Vrms.ModuleNumber = 0R
		Me.display_Vrms.Name = "display_Vrms"
		Me.display_Vrms.Size = New System.Drawing.Size(368, 113)
		Me.display_Vrms.TabIndex = 213
		Me.display_Vrms.Title_To_Display = "VRMS"
		Me.display_Vrms.Value_To_Display = 0R
		Me.display_Vrms.Visible = False
		'
		'display_dBm
		'
		Me.display_dBm.AllowDrop = True
		Me.display_dBm.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink
		Me.display_dBm.BackColor = System.Drawing.Color.Black
		Me.display_dBm.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
		Me.display_dBm.Dock = System.Windows.Forms.DockStyle.Fill
		Me.display_dBm.Location = New System.Drawing.Point(1104, 0)
		Me.display_dBm.Margin = New System.Windows.Forms.Padding(0)
		Me.display_dBm.ModuleNumber = 0R
		Me.display_dBm.Name = "display_dBm"
		Me.display_dBm.Size = New System.Drawing.Size(369, 113)
		Me.display_dBm.TabIndex = 214
		Me.display_dBm.Title_To_Display = "dBm"
		Me.display_dBm.Value_To_Display = 0R
		Me.display_dBm.Visible = False
		'
		'CheckBox_freq
		'
		Me.CheckBox_freq.AutoSize = True
		Me.CheckBox_freq.Dock = System.Windows.Forms.DockStyle.Left
		Me.CheckBox_freq.Location = New System.Drawing.Point(0, 113)
		Me.CheckBox_freq.Margin = New System.Windows.Forms.Padding(0)
		Me.CheckBox_freq.Name = "CheckBox_freq"
		Me.CheckBox_freq.Size = New System.Drawing.Size(55, 28)
		Me.CheckBox_freq.TabIndex = 234
		Me.CheckBox_freq.Text = "FREQ"
		Me.CheckBox_freq.UseVisualStyleBackColor = True
		'
		'CheckBox_VPP
		'
		Me.CheckBox_VPP.AutoSize = True
		Me.CheckBox_VPP.Dock = System.Windows.Forms.DockStyle.Left
		Me.CheckBox_VPP.Location = New System.Drawing.Point(368, 113)
		Me.CheckBox_VPP.Margin = New System.Windows.Forms.Padding(0)
		Me.CheckBox_VPP.Name = "CheckBox_VPP"
		Me.CheckBox_VPP.Size = New System.Drawing.Size(47, 28)
		Me.CheckBox_VPP.TabIndex = 235
		Me.CheckBox_VPP.Text = "VPP"
		Me.CheckBox_VPP.UseVisualStyleBackColor = True
		'
		'CheckBox_Vrms
		'
		Me.CheckBox_Vrms.AutoSize = True
		Me.CheckBox_Vrms.Dock = System.Windows.Forms.DockStyle.Left
		Me.CheckBox_Vrms.Location = New System.Drawing.Point(736, 113)
		Me.CheckBox_Vrms.Margin = New System.Windows.Forms.Padding(0)
		Me.CheckBox_Vrms.Name = "CheckBox_Vrms"
		Me.CheckBox_Vrms.Size = New System.Drawing.Size(49, 28)
		Me.CheckBox_Vrms.TabIndex = 236
		Me.CheckBox_Vrms.Text = "Vrms"
		Me.CheckBox_Vrms.UseVisualStyleBackColor = True
		'
		'display_freq
		'
		Me.display_freq.AllowDrop = True
		Me.display_freq.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink
		Me.display_freq.BackColor = System.Drawing.Color.Black
		Me.display_freq.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
		Me.display_freq.Dock = System.Windows.Forms.DockStyle.Fill
		Me.display_freq.Location = New System.Drawing.Point(0, 0)
		Me.display_freq.Margin = New System.Windows.Forms.Padding(0)
		Me.display_freq.ModuleNumber = 0R
		Me.display_freq.Name = "display_freq"
		Me.display_freq.Size = New System.Drawing.Size(368, 113)
		Me.display_freq.TabIndex = 215
		Me.display_freq.Title_To_Display = "Freq"
		Me.display_freq.Value_To_Display = 0R
		Me.display_freq.Visible = False
		'
		'TableLayoutPanel6
		'
		Me.TableLayoutPanel6.ColumnCount = 2
		Me.TableLayoutPanel6.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 33.33333!))
		Me.TableLayoutPanel6.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 66.66666!))
		Me.TableLayoutPanel6.Controls.Add(Me.CheckBox_graph, 0, 1)
		Me.TableLayoutPanel6.Controls.Add(Me.TrackBar_GraphDelay, 1, 1)
		Me.TableLayoutPanel6.Controls.Add(Me.TrackBar_Number_Of_Averages, 1, 0)
		Me.TableLayoutPanel6.Controls.Add(Me.CheckBox_Averaging, 0, 0)
		Me.TableLayoutPanel6.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TableLayoutPanel6.Location = New System.Drawing.Point(1107, 144)
		Me.TableLayoutPanel6.Name = "TableLayoutPanel6"
		Me.TableLayoutPanel6.RowCount = 2
		Me.TableLayoutPanel6.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel6.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel6.Size = New System.Drawing.Size(363, 91)
		Me.TableLayoutPanel6.TabIndex = 237
		'
		'CheckBox_graph
		'
		Me.CheckBox_graph.AutoSize = True
		Me.CheckBox_graph.Dock = System.Windows.Forms.DockStyle.Fill
		Me.CheckBox_graph.Location = New System.Drawing.Point(3, 48)
		Me.CheckBox_graph.Name = "CheckBox_graph"
		Me.CheckBox_graph.Size = New System.Drawing.Size(115, 40)
		Me.CheckBox_graph.TabIndex = 235
		Me.CheckBox_graph.Text = "GRAPH DELAY"
		Me.CheckBox_graph.UseVisualStyleBackColor = True
		'
		'TrackBar_GraphDelay
		'
		Me.TrackBar_GraphDelay.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TrackBar_GraphDelay.Location = New System.Drawing.Point(124, 48)
		Me.TrackBar_GraphDelay.Maximum = 50
		Me.TrackBar_GraphDelay.Name = "TrackBar_GraphDelay"
		Me.TrackBar_GraphDelay.Size = New System.Drawing.Size(236, 40)
		Me.TrackBar_GraphDelay.TabIndex = 233
		Me.TrackBar_GraphDelay.Value = 5
		'
		'TrackBar_Number_Of_Averages
		'
		Me.TrackBar_Number_Of_Averages.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TrackBar_Number_Of_Averages.Location = New System.Drawing.Point(124, 3)
		Me.TrackBar_Number_Of_Averages.Maximum = 100
		Me.TrackBar_Number_Of_Averages.Minimum = 1
		Me.TrackBar_Number_Of_Averages.Name = "TrackBar_Number_Of_Averages"
		Me.TrackBar_Number_Of_Averages.Size = New System.Drawing.Size(236, 39)
		Me.TrackBar_Number_Of_Averages.TabIndex = 0
		Me.TrackBar_Number_Of_Averages.Value = 25
		'
		'CheckBox_Averaging
		'
		Me.CheckBox_Averaging.AutoSize = True
		Me.CheckBox_Averaging.Location = New System.Drawing.Point(3, 3)
		Me.CheckBox_Averaging.Name = "CheckBox_Averaging"
		Me.CheckBox_Averaging.Size = New System.Drawing.Size(74, 17)
		Me.CheckBox_Averaging.TabIndex = 2
		Me.CheckBox_Averaging.Text = "Averaging"
		Me.CheckBox_Averaging.UseVisualStyleBackColor = True
		'
		'TableLayoutPanel2
		'
		Me.TableLayoutPanel2.ColumnCount = 1
		Me.TableLayoutPanel2.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 100.0!))
		Me.TableLayoutPanel2.Controls.Add(Me.TextBox_vertical, 0, 0)
		Me.TableLayoutPanel2.Controls.Add(Me.TrackBar_Vertical, 0, 1)
		Me.TableLayoutPanel2.Location = New System.Drawing.Point(736, 141)
		Me.TableLayoutPanel2.Margin = New System.Windows.Forms.Padding(0)
		Me.TableLayoutPanel2.Name = "TableLayoutPanel2"
		Me.TableLayoutPanel2.RowCount = 2
		Me.TableLayoutPanel2.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel2.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel2.Size = New System.Drawing.Size(368, 97)
		Me.TableLayoutPanel2.TabIndex = 236
		'
		'TextBox_vertical
		'
		Me.TextBox_vertical.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TextBox_vertical.Location = New System.Drawing.Point(0, 0)
		Me.TextBox_vertical.Margin = New System.Windows.Forms.Padding(0)
		Me.TextBox_vertical.Name = "TextBox_vertical"
		Me.TextBox_vertical.Size = New System.Drawing.Size(368, 20)
		Me.TextBox_vertical.TabIndex = 233
		'
		'TrackBar_Vertical
		'
		Me.TrackBar_Vertical.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TrackBar_Vertical.LargeChange = 1
		Me.TrackBar_Vertical.Location = New System.Drawing.Point(0, 48)
		Me.TrackBar_Vertical.Margin = New System.Windows.Forms.Padding(0)
		Me.TrackBar_Vertical.Maximum = 11
		Me.TrackBar_Vertical.Minimum = 1
		Me.TrackBar_Vertical.Name = "TrackBar_Vertical"
		Me.TrackBar_Vertical.Size = New System.Drawing.Size(368, 49)
		Me.TrackBar_Vertical.TabIndex = 231
		Me.TrackBar_Vertical.Value = 1
		'
		'TableLayoutPanel_MAIN
		'
		Me.TableLayoutPanel_MAIN.ColumnCount = 1
		Me.TableLayoutPanel_MAIN.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 100.0!))
		Me.TableLayoutPanel_MAIN.Controls.Add(Me.TableLayoutPanel1, 0, 1)
		Me.TableLayoutPanel_MAIN.Controls.Add(Me.TimeChart, 0, 0)
		Me.TableLayoutPanel_MAIN.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TableLayoutPanel_MAIN.Location = New System.Drawing.Point(0, 0)
		Me.TableLayoutPanel_MAIN.Margin = New System.Windows.Forms.Padding(0)
		Me.TableLayoutPanel_MAIN.Name = "TableLayoutPanel_MAIN"
		Me.TableLayoutPanel_MAIN.RowCount = 2
		Me.TableLayoutPanel_MAIN.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 75.0!))
		Me.TableLayoutPanel_MAIN.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 25.0!))
		Me.TableLayoutPanel_MAIN.Size = New System.Drawing.Size(1473, 950)
		Me.TableLayoutPanel_MAIN.TabIndex = 234
		'
		'TimeChart
		'
		Me.TimeChart.AllowDrop = True
		Me.TimeChart.BackColor = System.Drawing.Color.Black
		Me.TimeChart.BackSecondaryColor = System.Drawing.Color.Black
		Me.TimeChart.BorderlineColor = System.Drawing.Color.Maroon
		Me.TimeChart.BorderlineWidth = 0
		Me.TimeChart.BorderSkin.BackSecondaryColor = System.Drawing.Color.FromArgb(CType(CType(255, Byte), Integer), CType(CType(192, Byte), Integer), CType(CType(192, Byte), Integer))
		ChartArea1.BackColor = System.Drawing.Color.DimGray
		ChartArea1.BackSecondaryColor = System.Drawing.Color.FromArgb(CType(CType(64, Byte), Integer), CType(CType(64, Byte), Integer), CType(CType(64, Byte), Integer))
		ChartArea1.Name = "ChartArea1"
		Me.TimeChart.ChartAreas.Add(ChartArea1)
		Me.TimeChart.Cursor = System.Windows.Forms.Cursors.Cross
		Me.TimeChart.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TimeChart.Location = New System.Drawing.Point(0, 0)
		Me.TimeChart.Margin = New System.Windows.Forms.Padding(0)
		Me.TimeChart.MaximumSize = New System.Drawing.Size(5000, 5000)
		Me.TimeChart.MinimumSize = New System.Drawing.Size(100, 100)
		Me.TimeChart.Name = "TimeChart"
		Me.TimeChart.Palette = System.Windows.Forms.DataVisualization.Charting.ChartColorPalette.Fire
		Series1.BackSecondaryColor = System.Drawing.Color.Black
		Series1.ChartArea = "ChartArea1"
		Series1.ChartType = System.Windows.Forms.DataVisualization.Charting.SeriesChartType.Area
		Series1.Font = New System.Drawing.Font("Microsoft Sans Serif", 6.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Series1.IsVisibleInLegend = False
		Series1.Name = "Series1"
		Series1.Points.Add(DataPoint1)
		Me.TimeChart.Series.Add(Series1)
		Me.TimeChart.Size = New System.Drawing.Size(1473, 712)
		Me.TimeChart.TabIndex = 225
		Me.TimeChart.Text = "Chart1"
		Me.TimeChart.TextAntiAliasingQuality = System.Windows.Forms.DataVisualization.Charting.TextAntiAliasingQuality.SystemDefault
		'
		'Scope_Channel_Display
		'
		Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
		Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
		Me.Controls.Add(Me.TextBox_SCOPE_Title)
		Me.Controls.Add(Me.TableLayoutPanel_MAIN)
		Me.Name = "Scope_Channel_Display"
		Me.Size = New System.Drawing.Size(1473, 950)
		Me.ContextMenuStrip1.ResumeLayout(False)
		Me.TableLayoutPanel1.ResumeLayout(False)
		Me.TableLayoutPanel1.PerformLayout()
		Me.TableLayoutPanel4.ResumeLayout(False)
		Me.TableLayoutPanel4.PerformLayout()
		CType(Me.TrackBar_Horizontal, System.ComponentModel.ISupportInitialize).EndInit()
		Me.TableLayoutPanel3.ResumeLayout(False)
		Me.TableLayoutPanel6.ResumeLayout(False)
		Me.TableLayoutPanel6.PerformLayout()
		CType(Me.TrackBar_GraphDelay, System.ComponentModel.ISupportInitialize).EndInit()
		CType(Me.TrackBar_Number_Of_Averages, System.ComponentModel.ISupportInitialize).EndInit()
		Me.TableLayoutPanel2.ResumeLayout(False)
		Me.TableLayoutPanel2.PerformLayout()
		CType(Me.TrackBar_Vertical, System.ComponentModel.ISupportInitialize).EndInit()
		Me.TableLayoutPanel_MAIN.ResumeLayout(False)
		CType(Me.TimeChart, System.ComponentModel.ISupportInitialize).EndInit()
		Me.ResumeLayout(False)
		Me.PerformLayout()

	End Sub

	Friend WithEvents TextBox_SCOPE_Title As TextBox
	Friend WithEvents display_freq As Horizontal_Meter_With_Text
	Friend WithEvents display_dBm As Horizontal_Meter_With_Text
	Friend WithEvents display_Vrms As Horizontal_Meter_With_Text
	Friend WithEvents display_VPP As Horizontal_Meter_With_Text
	Friend WithEvents ContextMenuStrip1 As ContextMenuStrip
	Friend WithEvents ToolStripSeparator1 As ToolStripSeparator
	Friend WithEvents Button_RouteMe As Button
	Friend WithEvents Button_FFT As Button
	Friend WithEvents Button_Autoscale As Button
	Friend WithEvents TableLayoutPanel1 As TableLayoutPanel
	Friend WithEvents TableLayoutPanel3 As TableLayoutPanel
	Friend WithEvents CheckBox_freq As CheckBox
	Friend WithEvents CheckBox_VPP As CheckBox
	Friend WithEvents CheckBox_Vrms As CheckBox
	Friend WithEvents TableLayoutPanel_MAIN As TableLayoutPanel
	Friend WithEvents TableLayoutPanel4 As TableLayoutPanel
	Friend WithEvents TableLayoutPanel2 As TableLayoutPanel
	Friend WithEvents TextBox_TimeBase As TextBox
	Friend WithEvents TableLayoutPanel6 As TableLayoutPanel
	Friend WithEvents TrackBar_Number_Of_Averages As TrackBar
	Friend WithEvents CheckBox_Averaging As CheckBox
	Friend WithEvents TrackBar_GraphDelay As TrackBar
	Friend WithEvents CheckBox_graph As CheckBox
	Friend WithEvents TrackBar_Vertical As TrackBar
	Friend WithEvents TrackBar_Horizontal As TrackBar
	Friend WithEvents TimeChart As DataVisualization.Charting.Chart
	Friend WithEvents TextBox_vertical As TextBox
End Class
