<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()>
Partial Class DMMControl
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
		Me.ComboBox_DMM_function = New System.Windows.Forms.ComboBox()
		Me.MeasurementName = New System.Windows.Forms.TextBox()
		Me.Vertical_Meter = New APK_Bench_Software.Vertical_Meter()
		Me.TableLayoutPanel1 = New System.Windows.Forms.TableLayoutPanel()
		Me.TableLayoutPanel2 = New System.Windows.Forms.TableLayoutPanel()
		Me.Horizontal_Meter = New APK_Bench_Software.Horizontal_Meter_With_Text()
		Me.TableLayoutPanel1.SuspendLayout()
		Me.TableLayoutPanel2.SuspendLayout()
		Me.SuspendLayout()
		'
		'ComboBox_DMM_function
		'
		Me.ComboBox_DMM_function.Dock = System.Windows.Forms.DockStyle.Fill
		Me.ComboBox_DMM_function.FormattingEnabled = True
		Me.ComboBox_DMM_function.Items.AddRange(New Object() {"V DC", "I DC", "V AC", "I AC", "R 2W", "R 4W", "Diode", "Capacitance", "Freq", "Period", "Continuity"})
		Me.ComboBox_DMM_function.Location = New System.Drawing.Point(3, 23)
		Me.ComboBox_DMM_function.Name = "ComboBox_DMM_function"
		Me.ComboBox_DMM_function.Size = New System.Drawing.Size(833, 21)
		Me.ComboBox_DMM_function.TabIndex = 170
		Me.ComboBox_DMM_function.Text = "Function"
		'
		'MeasurementName
		'
		Me.MeasurementName.Dock = System.Windows.Forms.DockStyle.Fill
		Me.MeasurementName.Location = New System.Drawing.Point(3, 3)
		Me.MeasurementName.Name = "MeasurementName"
		Me.MeasurementName.Size = New System.Drawing.Size(833, 20)
		Me.MeasurementName.TabIndex = 174
		'
		'Vertical_Meter
		'
		Me.Vertical_Meter.Dock = System.Windows.Forms.DockStyle.Fill
		Me.Vertical_Meter.Location = New System.Drawing.Point(848, 3)
		Me.Vertical_Meter.ModuleNumber = 0R
		Me.Vertical_Meter.Name = "Vertical_Meter"
		Me.Vertical_Meter.Plot_V1 = 0R
		Me.Vertical_Meter.Plot_V2 = 0R
		Me.Vertical_Meter.Plot_V3 = 0R
		Me.Vertical_Meter.Plot_V4 = 0R
		Me.Vertical_Meter.Size = New System.Drawing.Size(839, 872)
		Me.Vertical_Meter.TabIndex = 173
		'
		'TableLayoutPanel1
		'
		Me.TableLayoutPanel1.ColumnCount = 2
		Me.TableLayoutPanel1.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel1.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel1.Controls.Add(Me.TableLayoutPanel2, 0, 0)
		Me.TableLayoutPanel1.Controls.Add(Me.Vertical_Meter, 1, 0)
		Me.TableLayoutPanel1.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TableLayoutPanel1.Location = New System.Drawing.Point(0, 0)
		Me.TableLayoutPanel1.Name = "TableLayoutPanel1"
		Me.TableLayoutPanel1.RowCount = 1
		Me.TableLayoutPanel1.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel1.Size = New System.Drawing.Size(1690, 878)
		Me.TableLayoutPanel1.TabIndex = 175
		'
		'TableLayoutPanel2
		'
		Me.TableLayoutPanel2.ColumnCount = 1
		Me.TableLayoutPanel2.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 100.0!))
		Me.TableLayoutPanel2.Controls.Add(Me.Horizontal_Meter, 0, 2)
		Me.TableLayoutPanel2.Controls.Add(Me.ComboBox_DMM_function, 0, 1)
		Me.TableLayoutPanel2.Controls.Add(Me.MeasurementName, 0, 0)
		Me.TableLayoutPanel2.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TableLayoutPanel2.Location = New System.Drawing.Point(3, 3)
		Me.TableLayoutPanel2.Name = "TableLayoutPanel2"
		Me.TableLayoutPanel2.RowCount = 3
		Me.TableLayoutPanel2.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 20.0!))
		Me.TableLayoutPanel2.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 20.0!))
		Me.TableLayoutPanel2.RowStyles.Add(New System.Windows.Forms.RowStyle())
		Me.TableLayoutPanel2.Size = New System.Drawing.Size(839, 872)
		Me.TableLayoutPanel2.TabIndex = 176
		'
		'Horizontal_Meter
		'
		Me.Horizontal_Meter.AllowDrop = True
		Me.Horizontal_Meter.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink
		Me.Horizontal_Meter.BackColor = System.Drawing.Color.Black
		Me.Horizontal_Meter.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
		Me.Horizontal_Meter.Dock = System.Windows.Forms.DockStyle.Fill
		Me.Horizontal_Meter.Location = New System.Drawing.Point(3, 43)
		Me.Horizontal_Meter.ModuleNumber = 0R
		Me.Horizontal_Meter.Name = "Horizontal_Meter"
		Me.Horizontal_Meter.Size = New System.Drawing.Size(833, 826)
		Me.Horizontal_Meter.TabIndex = 172
		Me.Horizontal_Meter.Title_To_Display = ""
		Me.Horizontal_Meter.Value_To_Display = 0R
		'
		'DMMControl
		'
		Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
		Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
		Me.Controls.Add(Me.TableLayoutPanel1)
		Me.Name = "DMMControl"
		Me.Size = New System.Drawing.Size(1690, 878)
		Me.TableLayoutPanel1.ResumeLayout(False)
		Me.TableLayoutPanel2.ResumeLayout(False)
		Me.TableLayoutPanel2.PerformLayout()
		Me.ResumeLayout(False)

	End Sub

	Friend WithEvents ComboBox_DMM_function As ComboBox
	Friend WithEvents Vertical_Meter As Vertical_Meter
	Friend WithEvents MeasurementName As TextBox
	Friend WithEvents TableLayoutPanel1 As TableLayoutPanel
	Friend WithEvents TableLayoutPanel2 As TableLayoutPanel
	Friend WithEvents Horizontal_Meter As Horizontal_Meter_With_Text
End Class
