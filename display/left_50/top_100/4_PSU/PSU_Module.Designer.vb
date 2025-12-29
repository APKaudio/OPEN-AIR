<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()>
Partial Class PSU_Module
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
		Me.PSU_Vset = New System.Windows.Forms.TextBox()
		Me.PSU_Iset = New System.Windows.Forms.TextBox()
		Me.Button_PSU_OutputEnable = New System.Windows.Forms.Button()
		Me.Display_Voltage = New APK_Bench_Software.Horizontal_Meter_With_Text()
		Me.Display_Current = New APK_Bench_Software.Horizontal_Meter_With_Text()
		Me.Display_Power = New APK_Bench_Software.Horizontal_Meter_With_Text()
		Me.Label_Voltage = New System.Windows.Forms.Label()
		Me.Label_Current = New System.Windows.Forms.Label()
		Me.TableLayoutPanel1 = New System.Windows.Forms.TableLayoutPanel()
		Me.TableLayoutPanel2 = New System.Windows.Forms.TableLayoutPanel()
		Me.TableLayoutPanel3 = New System.Windows.Forms.TableLayoutPanel()
		Me.TableLayoutPanel1.SuspendLayout()
		Me.TableLayoutPanel2.SuspendLayout()
		Me.TableLayoutPanel3.SuspendLayout()
		Me.SuspendLayout()
		'
		'PSU_Vset
		'
		Me.PSU_Vset.BackColor = System.Drawing.Color.Silver
		Me.PSU_Vset.Dock = System.Windows.Forms.DockStyle.Fill
		Me.PSU_Vset.Font = New System.Drawing.Font("Arial Black", 14.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.PSU_Vset.Location = New System.Drawing.Point(115, 3)
		Me.PSU_Vset.Name = "PSU_Vset"
		Me.PSU_Vset.Size = New System.Drawing.Size(107, 34)
		Me.PSU_Vset.TabIndex = 278
		Me.PSU_Vset.Text = "15"
		'
		'PSU_Iset
		'
		Me.PSU_Iset.BackColor = System.Drawing.Color.Silver
		Me.PSU_Iset.Dock = System.Windows.Forms.DockStyle.Fill
		Me.PSU_Iset.Font = New System.Drawing.Font("Arial Black", 14.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.PSU_Iset.Location = New System.Drawing.Point(115, 89)
		Me.PSU_Iset.Name = "PSU_Iset"
		Me.PSU_Iset.Size = New System.Drawing.Size(107, 34)
		Me.PSU_Iset.TabIndex = 279
		Me.PSU_Iset.Text = ".3"
		'
		'Button_PSU_OutputEnable
		'
		Me.Button_PSU_OutputEnable.BackColor = System.Drawing.Color.Gray
		Me.Button_PSU_OutputEnable.Dock = System.Windows.Forms.DockStyle.Fill
		Me.Button_PSU_OutputEnable.Font = New System.Drawing.Font("Arial Black", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Button_PSU_OutputEnable.Location = New System.Drawing.Point(234, 3)
		Me.Button_PSU_OutputEnable.Name = "Button_PSU_OutputEnable"
		Me.Button_PSU_OutputEnable.Size = New System.Drawing.Size(225, 172)
		Me.Button_PSU_OutputEnable.TabIndex = 280
		Me.Button_PSU_OutputEnable.Text = "OFF"
		Me.Button_PSU_OutputEnable.UseVisualStyleBackColor = False
		'
		'Display_Voltage
		'
		Me.Display_Voltage.AllowDrop = True
		Me.Display_Voltage.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink
		Me.Display_Voltage.BackColor = System.Drawing.Color.Black
		Me.Display_Voltage.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
		Me.Display_Voltage.Dock = System.Windows.Forms.DockStyle.Fill
		Me.Display_Voltage.Location = New System.Drawing.Point(471, 3)
		Me.Display_Voltage.ModuleNumber = 0R
		Me.Display_Voltage.Name = "Display_Voltage"
		Me.Display_Voltage.Size = New System.Drawing.Size(463, 178)
		Me.Display_Voltage.TabIndex = 281
		Me.Display_Voltage.Title_To_Display = "V"
		Me.Display_Voltage.Value_To_Display = 0R
		Me.Display_Voltage.Visible = False
		'
		'Display_Current
		'
		Me.Display_Current.AllowDrop = True
		Me.Display_Current.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink
		Me.Display_Current.BackColor = System.Drawing.Color.Black
		Me.Display_Current.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
		Me.Display_Current.Dock = System.Windows.Forms.DockStyle.Fill
		Me.Display_Current.Location = New System.Drawing.Point(3, 187)
		Me.Display_Current.ModuleNumber = 0R
		Me.Display_Current.Name = "Display_Current"
		Me.Display_Current.Size = New System.Drawing.Size(462, 178)
		Me.Display_Current.TabIndex = 282
		Me.Display_Current.Title_To_Display = "A"
		Me.Display_Current.Value_To_Display = 0R
		Me.Display_Current.Visible = False
		'
		'Display_Power
		'
		Me.Display_Power.AllowDrop = True
		Me.Display_Power.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink
		Me.Display_Power.BackColor = System.Drawing.Color.Black
		Me.Display_Power.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
		Me.Display_Power.Dock = System.Windows.Forms.DockStyle.Fill
		Me.Display_Power.Location = New System.Drawing.Point(471, 187)
		Me.Display_Power.ModuleNumber = 0R
		Me.Display_Power.Name = "Display_Power"
		Me.Display_Power.Size = New System.Drawing.Size(463, 178)
		Me.Display_Power.TabIndex = 283
		Me.Display_Power.Title_To_Display = "W"
		Me.Display_Power.Value_To_Display = 0R
		Me.Display_Power.Visible = False
		'
		'Label_Voltage
		'
		Me.Label_Voltage.AutoSize = True
		Me.Label_Voltage.Dock = System.Windows.Forms.DockStyle.Fill
		Me.Label_Voltage.Font = New System.Drawing.Font("Microsoft Sans Serif", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label_Voltage.Location = New System.Drawing.Point(3, 0)
		Me.Label_Voltage.Name = "Label_Voltage"
		Me.Label_Voltage.Size = New System.Drawing.Size(106, 86)
		Me.Label_Voltage.TabIndex = 284
		Me.Label_Voltage.Text = "V DC"
		'
		'Label_Current
		'
		Me.Label_Current.AutoSize = True
		Me.Label_Current.Dock = System.Windows.Forms.DockStyle.Fill
		Me.Label_Current.Font = New System.Drawing.Font("Microsoft Sans Serif", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label_Current.Location = New System.Drawing.Point(3, 86)
		Me.Label_Current.Name = "Label_Current"
		Me.Label_Current.Size = New System.Drawing.Size(106, 86)
		Me.Label_Current.TabIndex = 285
		Me.Label_Current.Text = "I DC"
		'
		'TableLayoutPanel1
		'
		Me.TableLayoutPanel1.ColumnCount = 2
		Me.TableLayoutPanel1.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel1.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel1.Controls.Add(Me.TableLayoutPanel2, 0, 0)
		Me.TableLayoutPanel1.Controls.Add(Me.Display_Current, 0, 1)
		Me.TableLayoutPanel1.Controls.Add(Me.Display_Power, 1, 1)
		Me.TableLayoutPanel1.Controls.Add(Me.Display_Voltage, 1, 0)
		Me.TableLayoutPanel1.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TableLayoutPanel1.Location = New System.Drawing.Point(0, 0)
		Me.TableLayoutPanel1.Name = "TableLayoutPanel1"
		Me.TableLayoutPanel1.RowCount = 2
		Me.TableLayoutPanel1.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel1.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel1.Size = New System.Drawing.Size(937, 368)
		Me.TableLayoutPanel1.TabIndex = 286
		'
		'TableLayoutPanel2
		'
		Me.TableLayoutPanel2.ColumnCount = 2
		Me.TableLayoutPanel2.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel2.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel2.Controls.Add(Me.Button_PSU_OutputEnable, 1, 0)
		Me.TableLayoutPanel2.Controls.Add(Me.TableLayoutPanel3, 0, 0)
		Me.TableLayoutPanel2.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TableLayoutPanel2.Location = New System.Drawing.Point(3, 3)
		Me.TableLayoutPanel2.Name = "TableLayoutPanel2"
		Me.TableLayoutPanel2.RowCount = 1
		Me.TableLayoutPanel2.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel2.Size = New System.Drawing.Size(462, 178)
		Me.TableLayoutPanel2.TabIndex = 287
		'
		'TableLayoutPanel3
		'
		Me.TableLayoutPanel3.ColumnCount = 2
		Me.TableLayoutPanel3.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel3.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel3.Controls.Add(Me.PSU_Iset, 1, 1)
		Me.TableLayoutPanel3.Controls.Add(Me.Label_Voltage, 0, 0)
		Me.TableLayoutPanel3.Controls.Add(Me.Label_Current, 0, 1)
		Me.TableLayoutPanel3.Controls.Add(Me.PSU_Vset, 1, 0)
		Me.TableLayoutPanel3.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TableLayoutPanel3.Location = New System.Drawing.Point(3, 3)
		Me.TableLayoutPanel3.Name = "TableLayoutPanel3"
		Me.TableLayoutPanel3.RowCount = 2
		Me.TableLayoutPanel3.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel3.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel3.Size = New System.Drawing.Size(225, 172)
		Me.TableLayoutPanel3.TabIndex = 288
		'
		'PSU_Module
		'
		Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
		Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
		Me.BackColor = System.Drawing.Color.Gray
		Me.Controls.Add(Me.TableLayoutPanel1)
		Me.Name = "PSU_Module"
		Me.Size = New System.Drawing.Size(937, 368)
		Me.TableLayoutPanel1.ResumeLayout(False)
		Me.TableLayoutPanel2.ResumeLayout(False)
		Me.TableLayoutPanel3.ResumeLayout(False)
		Me.TableLayoutPanel3.PerformLayout()
		Me.ResumeLayout(False)

	End Sub

	Friend WithEvents PSU_Vset As TextBox
	Friend WithEvents PSU_Iset As TextBox
	Friend WithEvents Button_PSU_OutputEnable As Button
	Public WithEvents Display_Voltage As Horizontal_Meter_With_Text
	Friend WithEvents Display_Current As Horizontal_Meter_With_Text
	Friend WithEvents Display_Power As Horizontal_Meter_With_Text
	Friend WithEvents Label_Voltage As Label
	Friend WithEvents Label_Current As Label
	Friend WithEvents TableLayoutPanel1 As TableLayoutPanel
	Friend WithEvents TableLayoutPanel2 As TableLayoutPanel
	Friend WithEvents TableLayoutPanel3 As TableLayoutPanel
End Class
