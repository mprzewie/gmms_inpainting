# 2021-04-19 23:15:17.274994
python train_wae.py --experiment_name=ae_v3/inp_dmfa_fc_comp_cnv --inpainter_type=dmfa --inpainter_path ../results/inpainting/svhn/fullconv/complete_data/dmfa_mse_10_eps/ --batch_size 64 --dataset svhn --img_size 32 --mask_hidden_h 16 --mask_hidden_w 16 --num_epochs=10 --render_every 2 --dataset_root /mnt/users/mprzewiezlikowski/local/data/.data/ --lr 4e-4 --wae_recon_loss mse --wae_bl 2 --wae_depth 2 --max_benchmark_batches -1 --wae_latent_size 60 --wae_fc 32 --wae_lc 96 --wae_disc_loss_weight 0 --skip_fid --convar_type naive
