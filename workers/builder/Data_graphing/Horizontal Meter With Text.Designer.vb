<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()>
Partial Class Horizontal_Meter_With_Text
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
        Me.Label_Value = New System.Windows.Forms.Label()
        Me.Label_Title = New System.Windows.Forms.Label()
        Me.BarGraphValue1 = New System.Windows.Forms.ProgressBar()
        Me.BarGraphValueDec = New System.Windows.Forms.ProgressBar()
        Me.Label1 = New System.Windows.Forms.Label()
        Me.Labeldec = New System.Windows.Forms.Label()
        Me.SuspendLayout()
        '
        'Label_Value
        '
        Me.Label_Value.AutoSize = True
        Me.Label_Value.Location = New System.Drawing.Point(3, 2)
        Me.Label_Value.Name = "Label_Value"
        Me.Label_Value.Size = New System.Drawing.Size(66, 13)
        Me.Label_Value.TabIndex = 15
        Me.Label_Value.Text = "Label_Value"
        '
        'Label_Title
        '
        Me.Label_Title.AutoSize = True
        Me.Label_Title.Location = New System.Drawing.Point(3, 29)
        Me.Label_Title.Name = "Label_Title"
        Me.Label_Title.Size = New System.Drawing.Size(59, 13)
        Me.Label_Title.TabIndex = 16
        Me.Label_Title.Text = "Label_Title"
        Me.Label_Title.TextAlign = System.Drawing.ContentAlignment.TopRight
        '
        'BarGraphValue1
        '
        Me.BarGraphValue1.ForeColor = System.Drawing.SystemColors.Desktop
        Me.BarGraphValue1.Location = New System.Drawing.Point(0, 0)
        Me.BarGraphValue1.Name = "BarGraphValue1"
        Me.BarGraphValue1.Size = New System.Drawing.Size(400, 15)
        Me.BarGraphValue1.Style = System.Windows.Forms.ProgressBarStyle.Continuous
        Me.BarGraphValue1.TabIndex = 17
        '
        'BarGraphValueDec
        '
        Me.BarGraphValueDec.Location = New System.Drawing.Point(0, 21)
        Me.BarGraphValueDec.Margin = New System.Windows.Forms.Padding(0)
        Me.BarGraphValueDec.Name = "BarGraphValueDec"
        Me.BarGraphValueDec.Size = New System.Drawing.Size(400, 15)
        Me.BarGraphValueDec.Style = System.Windows.Forms.ProgressBarStyle.Continuous
        Me.BarGraphValueDec.TabIndex = 18
        '
        'Label1
        '
        Me.Label1.AutoSize = True
        Me.Label1.Location = New System.Drawing.Point(405, 8)
        Me.Label1.Name = "Label1"
        Me.Label1.Size = New System.Drawing.Size(39, 13)
        Me.Label1.TabIndex = 20
        Me.Label1.Text = "Label1"
        '
        'Labeldec
        '
        Me.Labeldec.AutoSize = True
        Me.Labeldec.Location = New System.Drawing.Point(405, 24)
        Me.Labeldec.Name = "Labeldec"
        Me.Labeldec.Size = New System.Drawing.Size(39, 13)
        Me.Labeldec.TabIndex = 21
        Me.Labeldec.Text = "Label1"
        '
        'Horizontal_Meter_With_Text
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.Controls.Add(Me.Labeldec)
        Me.Controls.Add(Me.Label1)
        Me.Controls.Add(Me.Label_Title)
        Me.Controls.Add(Me.Label_Value)
        Me.Controls.Add(Me.BarGraphValue1)
        Me.Controls.Add(Me.BarGraphValueDec)
        Me.Name = "Horizontal_Meter_With_Text"
        Me.Size = New System.Drawing.Size(483, 41)
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub

    Friend WithEvents Title As Label
    Friend WithEvents VALUE As Label
    Friend WithEvents Label_Value As Label
    Friend WithEvents Label_Title As Label
    Friend WithEvents BarGraphValue1 As ProgressBar
    Friend WithEvents BarGraphValueDec As ProgressBar
    Friend WithEvents Label1 As Label
    Friend WithEvents Labeldec As Label
End Class
